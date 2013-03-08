from flask import Flask, render_template
import database
import register


# ToDo: Put app config in a config!
app = Flask(__name__)
app.secret_key = "gocu5eYoosh8oocoozeeG9queeghae7ushahp9ufaighoo5gex1vulaexohtepha"
database.init_session()
app.register_blueprint(register.bp, url_prefix='/register')


@app.teardown_request
def session_cleanup(_):
    database.session.remove()


@app.route("/")
def start():
    return render_template("start.html")


if __name__ == "__main__":
    app.debug = True
    app.run()
