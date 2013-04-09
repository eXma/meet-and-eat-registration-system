import os

from flask import Flask, render_template, redirect, url_for
from flask.ext.mail import Mail

import database


#todo http://pythonhosted.org/Flask-ErrorMail/
from webapp import admin, public, register
from webapp.dummy_data import make_dummy_data


EXAMPLE_CONFIG = "config_example"
PRODUCTIVE_CONFIG = "config"


def configure_app(app):
    """Apply the configuration data from the config module to the flask application.

    :type app: flask.Flask
    :param app: The Application to configure.
    """
    filename = EXAMPLE_CONFIG
    if os.path.isfile(os.path.join(os.path.dirname(__file__), "cfg", "%s.py" % PRODUCTIVE_CONFIG)):
        filename = PRODUCTIVE_CONFIG

    app.config.from_object("webapp.cfg.%s" % filename)


def init_app(app):
    """Initialize the given Flask application.

    :type app: flask.Flask
    :param app: The application to configure.
    :rtype: flask.Flask
    :return: The configured application.
    """
    configure_app(app)
    database.init_session(connection_string=app.config["DB_CONNECTION"])
    app.register_blueprint(register.bp, url_prefix='/register')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(public.bp, url_prefix='/public')

    app.mail = Mail(app)
    #make_dummy_data(30)

    @app.teardown_request
    def session_cleanup(_):
        database.session.remove()

    @app.route("/")
    def start():
        return redirect(url_for("register.form"))

    return app


if __name__ == "__main__":
    app = Flask(__name__)
    init_app(app)
    app.run()
