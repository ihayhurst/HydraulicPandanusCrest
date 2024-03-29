from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object("config.Production")
    # Override config with instance if present
    app.config.from_pyfile("flask.cfg", silent=True)

    # Initialise Plugins
    from .extensions import mail

    mail.init_app(app)

    with app.app_context():

        from .website.views import website
        from .api.views import api_pages
        from .errors import errors

        app.register_blueprint(website, url_prefix="/")
        app.register_blueprint(api_pages, url_prefix="/api")
        app.register_blueprint(errors)
    return app
