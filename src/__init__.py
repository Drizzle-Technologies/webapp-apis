"""Initialize Flask app."""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from .database.database import db

from .errors.AuthError import AuthError


def init_app():
    """Construct core Flask application with embedded Dash app."""
    # Instantiating Flask class. It will allow us to start our webapp.
    app = Flask(__name__, instance_relative_config=False)

    CORS(app)

    # Setting configs // Example config.DevelopmentConfig
    app.config.from_object(os.environ['APP_SETTINGS'])

    # Database connected to the app
    db.init_app(app)

    with app.app_context():
        # Creates database tables if they don't already exist
        db.create_all()

        # Registering all blueprints
        from .errors import bp as errors_bp
        app.register_blueprint(errors_bp)

        from .routes import api
        app.register_blueprint(api, url_prefix='/api')

        return app
