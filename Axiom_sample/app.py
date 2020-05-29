"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
"""
Flask Sample APIs
"""
from flask import Flask, jsonify, request,session, flash, render_template, make_response
import jwt
import datetime
from flask_dotenv import DotEnv
from apis.public import public_api
from apis.private import private_api
from apis.role import role_api
from apis.permission import permission_api
from axioms_flask.error import AxiomsError
from flask_cors import CORS
from functools import wraps

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
#@app.route("/", methods=["GET"])
#def index():
#    """
#    Index for this app
#    """
#    return jsonify({"api": "Flask Sample APIs"})



# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

app.config['SECRET_KEY']="ThisismyAxiomsSecretKey"
def check_for_token(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        token=request.args.get('token')
        if not token:
            return jsonify({'message':'Missing Token'}),403
        try:
            data=jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'Invalid token'}),403
        return func(*args,**kwargs)
    return wrapped

# Axioms Login route
@app.route('/')
def home():
    return "Welcome to Axioms.io. Authenticate and authorize your users. Add strong authentication, fine-grained authorization in your apps, devices, and APIs within a matter of hours."
#def index():
#    if not session.get("Logged in: "):
#        return render_template('login.html')
#    else:
#        return 'Currently Logged In'

@app.route('/auth')
@check_for_token
def authorised():
    return 'The data you are seeing right now is sensitive data and it\'s only seen after validating the token credentials'


@app.route('/login')
def login():
    auth=request.authorization
    if auth and auth.password=="password":
        token=jwt.encode(
            {
            'user': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60)
            },
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('utf-8')})
    return make_response("Could not verify",401,{'WWW-Authenticate':'Basic realm="login Required"'})

    #if request.form['username'] and request.form['password']=='password':
    #    session['logged in']==True
    #    token=jwt.encode(
    #        {
    #        'user': request.form['username'],
    #        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
    #        },
    #        app.config['SECRET_KEY'])
    #    return jsonify({'token': token.decode('utf-8')})
    #else:
    #    return make_response('Unable to verify',403, {'WWW-Authenticate':'Basic Real : Login '})

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
