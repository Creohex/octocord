import os, socket, json
from flask import Flask, request
from OpenSSL import SSL
from werkzeug.serving import make_ssl_devcert
from functools import wraps
import pymysql, uuid, requests, time, datetime, socket
import run_tests


# env variables:
required_variables = [
    'use_https',
    'db_host',
    'db_username',
    'db_password'
]
missing_variables = [_ for _ in required_variables if _ not in os.environ.keys()]
if len(missing_variables) > 0:
    raise Exception("Error: missing required variables: %s" % missing_variables)

# params:
USE_DEBUG = True
USE_HTTPS = False if os.environ['use_https'] == 'false' else True
db_host = os.environ['db_host']
db_db = 'octocord'
db_user = os.environ['db_username']
db_pass = os.environ['db_password']
app = Flask(__name__)

# certs:
if USE_HTTPS:
    if 'key.crt' not in os.listdir('/certs'):
        raise Exception("Couldn't find key.crt in /certs directory.")
    elif 'key.key' not in os.listdir('/certs'):
        raise Exception("Couldn't find key.key in /certs directory.")


# common functions:
def uuid_is_valid(id, ver=4):
    """ Check if uuid is a valid uuid version 1 """
    try:
        value = uuid.UUID(id, version=ver)
    except ValueError:
        return False
    return value.hex == id

def check_headers(req):
    """ check if required headers are valid and exist in database """
    if 'UUID' not in req.headers or 'UUID_SECRET' not in req.headers:
        raise Exception("Error: missing required headers (UUID / UUID_SECRET)")
    if not uuid_is_valid(req.headers['UUID']) or not uuid_is_valid(req.headers['UUID_SECRET']):
        raise Exception("Error invalid UUID/UUID_SECRET format")
    users = User.get_users()
    user = next((u for u in users if u.uuid == req.headers['UUID']), None)
    if user is None:
        raise Exception("Error: no user with such id (%s)" % req.headers['UUID'])
    elif user.uuid_secret != req.headers['UUID_SECRET']:
        raise Exception("Error: secret mismatch")
    return user


# db operations:
def db_connector():
    return pymysql.connect(host=db_host, port=3306, user=db_user, passwd=db_pass, db=db_db)

def query_db(query):
    """ queries local db and returns cursor containing data """
    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.close()
    return cursor

def query_db_commit(query):
    """ queries local db, commits any changes and returns cursor containing data (or changes) """
    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()
    return cursor


# query processing:
@app.route("/")
def list_api():
    """ root call """
    return "boo"

@app.route("/test")
def test():
    """ test.. """
    check_headers(request)
    return str(request.headers)

@app.route("/register", methods=['POST'])
def register_user():
    """ register new user """
    return json.dumps(User.add(payload).as_json())

@app.route("/hook")
def hook_list():
    check_headers(request)
    return json.dumps({"hooks": [_.as_json() for _ in Hook.get_hooks(request.headers['UUID'])]})

@app.route("/hook/add", methods=['POST'])
def hook_add():
    user = check_headers(request)
    user.add_hook(request.get_json())
    return json.dumps({"result": "ok"})

@app.route("/hook/<hook_uuid>", methods=['DELETE'])
def hook_del(hook_uuid):
    user = check_headers(request)
    hooks = Hook.get_hooks(user.uuid)
    hook = next((_ for _ in hooks if _.id == hook_uuid), None)
    if hook is not None:
        hook.delete()
        return "deleted"
    else:
        raise Exception("No hook with this id exists")

@app.route("/hook/<hook_uuid>", methods=['POST'])
def hook_post(hook_uuid):
    user = check_headers(request)
    hook = Hook.get_hook(hook_uuid)
    payload = request.get_json()
    try:
        requests.post(
            url=hook.get_link(),
            params={},
            json=Message.test()
        )
        return("ok")
    except Exception as e:
        raise Exception("hook_post() error: %s" % str(e))


# objects:
class User():
    def __init__(self, uuid, name, uuid_secret):
        self.uuid = uuid
        self.name = name
        self.uuid_secret = uuid_secret

    def __str__(self):
        return("User '%s': %s / %s" % (self.name, self.uuid, self.uuid_secret))

    def as_json(self):
        return {"uuid": self.uuid, "name": self.name, "uuid_secret": self.uuid_secret}

    def get_bots(self):
        pass

    def add_hook(self, payload):
        """ add new hook for this user """
        Hook.add(payload, self.uuid)

    def get_hooks(self):
        return Hook.get_hooks(self.uuid)

    @staticmethod
    def add(payload):
        # check payload / existing users
        payload = request.get_json()
        if "username" not in payload.keys():
            raise Exception("'username' field required in payload")
        new_username = payload['username']
        users = User.get_users()
        if next((_ for _ in users if _.name == new_username), None) is not None:
            raise Exception("User with this name already exists")

        # generate id/secret
        new_user = User(uuid.uuid4().hex, new_username, uuid.uuid4().hex)

        # update db
        query_db_commit("INSERT INTO user (id, name, secret) VALUES ('%s', '%s', '%s')"
                        % (new_user.uuid, new_user.name, new_user.uuid_secret))

        return new_user

    @staticmethod
    def exists(uuid):
        return query_db("SELECT * FROM user WHERE id = '%s'" % uuid).rowcount != 0

    @staticmethod
    def get_users():
        return [User(id.lower(), name, secret.lower()) for id, name, secret
                in query_db("SELECT id, name, secret FROM user")]


class Bot():
    def __init__(self):
        pass

    def __str__(self):
        pass


class Hook():
    def __init__(self, id, name, channel_id, token, avatar, guild_id, owner_id):
        self.id = id
        self.name = name
        self.channel_id = channel_id
        self.token = token
        self.avatar = avatar
        self.guild_id = guild_id
        self.owner_id = owner_id

    def __str__(self):
        print("%s (%s)" % (self.name, self.id))

    def as_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "channel_id": self.channel_id,
            "token": self.token,
            "avatar": self.avatar,
            "guild_id": self.guild_id,
            "owner_id": self.owner_id
        }

    def get_link(self):
        return "https://discordapp.com/api/webhooks/%s/%s" % (self.id, self.token)

    @staticmethod
    def add(payload, user_id):
        # check user
        if not User.exists(user_id):
            raise Exception("Hook.add() exception: no such user exists")

        # check payload for required parameters
        missing_parameters = (False, [])
        for field in Hook.required_fields():
            if field not in payload.keys():
                missing_parameters[0] = True
                missing_parameters[1].append(field)
        if missing_parameters[0]:
            raise Exception("Error: missing parameters (%s)" % ', '.join(missing_parameters[1]))

        # check if such hook already exists
        if Hook.exists(payload['id']):
            raise Exception("Hook with this id already exists in database")

        # add hook object
        id = uuid.uuid4().hex
        query_db_commit("INSERT INTO hook (id, name, channel_id, token, avatar, guild_id, owner_id) "
                        "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
                        % (payload['id'], payload['name'], payload['channel_id'], payload['token'],
                           payload['avatar'], payload['guild_id'], user_id))

        return "ok"

    def delete(self):
        query_db_commit("DELETE FROM hook WHERE id = '%s'" % self.id)

    @staticmethod
    def exists(id):
        """ check if hook with 'id' exists """
        return query_db("SELECT * FROM hook WHERE id = '%s'" % id).rowcount != 0

    @staticmethod
    def required_fields():
        return ['id', 'name', 'channel_id', 'token', 'avatar', 'guild_id']

    @staticmethod
    def get_hooks(owner_uuid):
        return [Hook(ID.lower(), name, channel_id, token, avatar, guild_id, owner_id.lower())
                for ID, name, channel_id, token, avatar, guild_id, owner_id
                in query_db("SELECT id, name, channel_id, token, avatar, guild_id, owner_id "
                            "FROM hook WHERE owner_id = '%s'" % owner_uuid)]

    @staticmethod
    def get_hook(uuid):
        return next(Hook(id, name, channel_id, token, avatar, guild_id, owner_id)
                    for id, name, channel_id, token, avatar, guild_id, owner_id
                    in query_db("SELECT id, name, channel_id, token, avatar, guild_id, owner_id "
                                "FROM hook WHERE id = '%s'" % uuid))

class Message:
    @staticmethod
    def simple(text):
        return {"content": text}

    @staticmethod
    def test():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
        s.close()
        return {"content": "This is a test message issued from %s (%s) at %s (%s)"
                           % (socket.gethostname(), addr, datetime.datetime.now(),
                              datetime.timezone(datetime.timedelta()))}


# server start
if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=USE_DEBUG,
            port=(443 if USE_HTTPS else 80),
            ssl_context=(('/certs/key.crt', '/certs/key.key') if USE_HTTPS else None))
