import os

from flask import Flask, render_template
from flask.ext.mail import Mail

import database
import register


#todo http://pythonhosted.org/Flask-ErrorMail/
from webapp import admin


EXAMPLE_CONFIG = "config_example"
PRODUCTIVE_CONFIG = "config"


def configure_app(app):
    """Apply the configuration data from the config module to the flask application.

    :type app: flask.Flask
    :param app: The Application to configure.
    """
    filename = EXAMPLE_CONFIG
    if os.path.isfile(os.path.join("cfg", "%s.py" % PRODUCTIVE_CONFIG)):
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

    app.mail = Mail(app)

    @app.teardown_request
    def session_cleanup(_):
        database.session.remove()

    @app.route("/")
    def start():
        return render_template("start.html")

    return app


if __name__ == "__main__":
    app = Flask(__name__)
    init_app(app)
    app.run()
