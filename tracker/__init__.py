import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt


jwt = JWTManager()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='your_strong_secret_key',
        JWT_SECRET_KEY='Yedije@13',
        JWT_TOKEN_LOCATION='headers',
        DATABASE=os.path.join(app.instance_path, 'expense.sqlite'),
    )

    jwt.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import expense
    app.register_blueprint(expense.bp)
    # app.add_url_rule('/', endpoint='expenses')


    return app