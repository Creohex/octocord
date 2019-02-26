import os, socket, json
from flask import Flask, request
from OpenSSL import SSL
from werkzeug.serving import make_ssl_devcert
from functools import wraps
import pymysql
import uuid
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
    if 'UUID' not in req.headers and 'UUID_SECRET' not in req.headers:
        raise Exception("Error: missing required headers (UUID / UUID_SECRET)")
    if not uuid_is_valid(req.headers['UUID']) or not uuid_is_valid(req.headers['UUID_SECRET']):
        raise Exception("Error invalid UUID/UUID_SECRET format")
    users = User.get_users()
    user = next((u for u in users if u.uuid == req.headers['UUID']), None)
    if user is None:
        raise Exception("Error: no user with such id (%s)" % req.headers['UUID'])
    elif user.uuid_secret != req.headers['UUID_SECRET']:
        raise Exception("Error: secret mismatch")


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
    """ ... """
    check_headers(request)
    return str(request.headers)

@app.route("/register", methods=['POST'])
def register_user():
    """ register new user """
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
    query_db_commit("INSERT INTO user (id, name, secret) VALUES (UNHEX('%s'), '%s', UNHEX('%s'))"
                    % (new_user.uuid, new_user.name, new_user.uuid_secret))
    return json.dumps(new_user.as_json())


# objects:
class User():
    def __init__(self, uuid, name, uuid_secret):
        self.uuid = uuid
        self.name = name
        self.uuid_secret = uuid_secret

    def __str__(self):
        return("User '%s': %s / %s" % (self.name, self.uuid, self.uuid_secret))

    def as_json(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "uuid_secret": self.uuid_secret
        }

    def get_bots(self):
        pass

    def get_hooks(self):
        pass

    @staticmethod
    def get_users():
        return [User(id, name, secret) for id, name, secret
                in query_db("SELECT id, name, secret FROM user")]


class Bot():
    def __init__(self):
        pass

    def __str__(self):
        pass


class Hook():
    def __init__(self, id, name, link, obj):
        pass

    def __str__(self):
        pass


# server start
if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=USE_DEBUG,
            port=(443 if USE_HTTPS else 80),
            ssl_context=(('/certs/key.crt', '/certs/key.key') if USE_HTTPS else None))
