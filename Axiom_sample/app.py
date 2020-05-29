"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
"""
Flask Sample APIs
"""
from flask import Flask, jsonify
from flask_dotenv import DotEnv
from apis.public import public_api
from apis.private import private_api
from apis.role import role_api
from apis.permission import permission_api
from axioms_flask.error import AxiomsError
from flask_cors import CORS

from os import environ

# Flask app
app = Flask(__name__)  # pylint: disable=invalid-name

app.config.from_object("config")

# if .env file available
env = DotEnv(app)

# else use environment variables
if environ.get('AXIOMS_DOMAIN', None):
    app.config['AXIOMS_DOMAIN'] = environ.get('AXIOMS_DOMAIN', None)
if environ.get('AXIOMS_AUDIENCE', None):
    app.config['AXIOMS_AUDIENCE'] = environ.get('AXIOMS_AUDIENCE', None)

# Setup CORS globally
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# API blueprints, imported after OS.environ
app.register_blueprint(public_api)
app.register_blueprint(private_api)
app.register_blueprint(role_api)
app.register_blueprint(permission_api)


@app.errorhandler(AxiomsError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    if ex.status_code == 401:
        response.headers[
            "WWW-Authenticate"
        ] = "Bearer realm='{}', error='{}', error_description='{}'".format(
            app.config["AXIOMS_DOMAIN"], ex.error["error"], ex.error["error_description"]
        )
    return response


# Controllers API
@app.route("/", methods=["GET"])
def index():
    """
    Index for this app
    """
    return jsonify({"api": "Flask Sample APIs"})


@app.route("/axioms_login")
def login():
    return "Welcome to Axiom_login Page"



# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app




if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
