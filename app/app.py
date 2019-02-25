import os, socket, json
from flask import Flask, request
from OpenSSL import SSL
from werkzeug.serving import make_ssl_devcert




# env variables:
required_variables = [
    'use_https',
    'db_username',
    'db_password'
]
missing_variables = [_ for _ in required_variables if _ not in os.environ.keys()]
if len(missing_variables) > 0:
    raise Exception("Error: missing required variables: %s" % missing_variables)

# params:
USE_DEBUG = True
USE_HTTPS = False if os.environ['use_https'] == 'false' else True
app = Flask(__name__)

# certs:
if USE_HTTPS:
    if 'key.crt' not in os.listdir('/certs'):
        raise Exception("Couldn't find key.crt in /certs directory.")
    elif 'key.key' not in os.listdir('/certs'):
        raise Exception("Couldn't find key.key in /certs directory.")


@app.route("/")
def list_api():
    return "boo"

@app.route("/test")
def test():
    return str(request.headers)


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            debug=USE_DEBUG,
            port=(443 if USE_HTTPS else 80),
            ssl_context=(('/certs/key.crt', '/certs/key.key') if USE_HTTPS else None))
