from flask import Flask, render_template
import database
import register
import os


EXAMPLE_CONFIG = "config_example"
PRODUCTIVE_CONFIG = "config"


def configure_app(app):
    filename = EXAMPLE_CONFIG
    if os.path.isfile(PRODUCTIVE_CONFIG):
        filename = PRODUCTIVE_CONFIG

    app.config.from_object("webapp.cfg.%s" % filename)


def init_app(app):
    configure_app(app)
    #app.secret_key = "gocu5eYoosh8oocoozeeG9queeghae7ushahp9ufaighoo5gex1vulaexohtepha"
    database.init_session()
    app.register_blueprint(register.bp, url_prefix='/register')

    @app.teardown_request
    def session_cleanup(_):
        database.session.remove()

    @app.route("/")
    def start():
        return render_template("start.html")


if __name__ == "__main__":
    app = Flask(__name__)
    init_app(app)
    app.debug = True
    app.run()
