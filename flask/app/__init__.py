from flask import Flask
from .website.views import website
from .api.views import api_pages
from .errors import errors

# from extensidbons import *
# Set Globals


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.Production")
    app.config.from_pyfile('config.py')

    with app.app_context():
        app.register_blueprint(website, url_prefix="/")
        app.register_blueprint(api_pages, url_prefix="/api")
        app.register_blueprint(errors)
    return app
