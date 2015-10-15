from datetime import datetime
import os
from logging import Formatter, getLogger

from flask import Flask, render_template, redirect, url_for
from flask.ext.mail import Mail

import database
from cfg import parse_end_date
from webapp import admin, public, register
from webapp.dummy_data import make_dummy_data
from webapp.reverse_proxy_wrapper import ReverseProxied


EXAMPLE_CONFIG = "config_example"
PRODUCTIVE_CONFIG = "config"


def configure_app(app):
    """Apply the configuration data from the config module to the flask application.

    :type app: flask.Flask
    :param app: The Application to configure.
    """
    filename = EXAMPLE_CONFIG
    if os.path.isfile(os.path.join(os.path.dirname(__file__), "..", "cfg", "%s.py" % PRODUCTIVE_CONFIG)):
        filename = PRODUCTIVE_CONFIG

    app.config.from_object("cfg.%s" % filename)


def init_logging(app):
    """Initialize app error logging

    :type app: flask.Flask
    :param app: The application to configure.
    """
    if app.debug:
        return

    ADMINS = ['meetandeat@exmatrikulationsamt.de']
    import logging
    from logging.handlers import SMTPHandler

    credentials = None
    secure = None
    if app.config.get("MAIL_USERNAME") is not None:
        credentials = (app.config["MAIL_USERNAME"], app.config.get("MAIL_PASSWORD"))
        if app.config.get("MAIL_USE_TLS") is not None or app.config.get("MAIL_USE_SSL") is not None:
            secure = tuple()

    mail_handler = SMTPHandler(app.config["MAIL_SERVER"],
                               app.config["ERROR_SENDER"],
                               app.config["ERROR_ADDRESS"],
                               app.config["ERROR_SUBJECT"],
                               credentials=credentials, secure=secure)

    mail_handler.setLevel(logging.ERROR)
    if app.config.get("ERROR_FORMAT") is not None:
        mail_handler.setFormatter(Formatter(app.config["ERROR_FORMAT"]))

    for log in (getLogger('sqlalchemy'), app.logger):
        log.addHandler(mail_handler)


def init_app(app):
    """Initialize the given Flask application.

    :type app: flask.Flask
    :param app: The application to configure.
    :rtype: flask.Flask
    :return: The configured application.
    """
    configure_app(app)
    init_logging(app)
    database.init_session(connection_string=app.config["DB_CONNECTION"])
    app.register_blueprint(register.bp, url_prefix='/register')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(public.bp, url_prefix='/public')

    app.mail = Mail(app)
    #make_dummy_data(30)

    app.config["REGISTER_END"] = parse_end_date(app.config["REGISTER_END"])

    @app.teardown_request
    def session_cleanup(_):
        database.session.remove()

    @app.route("/")
    def start():
        return redirect(url_for("register.form"))

    return app


app = Flask(__name__)
init_app(app)

if __name__ == "__main__":
    app.run("0.0.0.0")
else:
    if app.config.get("BEHIND_REVERSE_PROXY") is True:
        app = ReverseProxied(app)
