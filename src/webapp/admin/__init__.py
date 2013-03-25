from flask import current_app, session, redirect, url_for, render_template, Blueprint
from webapp.admin.login import delete_token, set_token, valid_admin
from webapp.forms import AdminLoginForm


bp = Blueprint('admin', __name__)


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if current_app.config["ADMIN_USER"] == form.login.data and current_app.config[
            "ADMIN_PASSWORD"] == form.password.data:
            set_token()

            return redirect(session.get("next") or url_for(".overview"))

    return render_template("admin/login.html", form=form)


@bp.route("/logout")
def logout():
    delete_token()
    redirect(url_for(".login"))


@bp.route("/")
@valid_admin
def overview():
    return "Working"

