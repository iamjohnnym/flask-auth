# ./service/__init__.py

import os
from flask import Flask, Blueprint
from flask_restplus import Api
from flask_praetorian import PraetorianError
from service.api.extensions import db, migrate, cors, toolbar, guard
from service.api.models import User


api_bp = Blueprint('api', __name__, url_prefix='/api')
rp_api = Api(api_bp)
# flask-praetorian is not compatible with flask-restplus errors without this
PraetorianError.register_error_handler_with_flask_restplus(rp_api)


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)
    app.debug = True

    # set config
    app_settings = os.getenv('APP_SETTINGS', 'service.config.TestingConfig')
    app.config.from_object(app_settings)

    # set up extensions
    cors.init_app(app)
    guard.init_app(app, User)
    db.init_app(app)
    migrate.init_app(app, db)

    if app.config['DEBUG_TB_ENABLED']:
        toolbar.init_app(app)

    # register blueprints
    from service.api.users import ns as users
    from service.api.auth import ns as auth

    app.register_blueprint(api_bp)
    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
