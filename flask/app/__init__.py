from flask import Flask
from .website.views import website
from .invapi.views import invapi

# from extensidbons import *
# Set Globals


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object("config.Production")

    with app.app_context():
        app.register_blueprint(website, url_prefix="/")
        app.register_blueprint(invapi, url_prefix="/invapi")
    return app
