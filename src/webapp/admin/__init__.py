import json
from math import floor
from flask import current_app, session, redirect, url_for, render_template, Blueprint
from database.model import Team
from webapp.admin.login import delete_token, set_token, valid_admin
from webapp.forms import AdminLoginForm

import database as db

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
@valid_admin
def logout():
    delete_token()
    return redirect(url_for(".login"))


@bp.route("/")
@valid_admin
def overview():
    return render_template("admin/base.html")


@bp.route("/map")
@valid_admin
def team_map():
    return render_template("admin/map.html")


_color_map = ["blue", "yellow", "green", "red"]


@bp.route("/map_teams")
@valid_admin
def map_teams():
    teams = db.session.query(Team).order_by(Team.id).all()
    data = []

    max_working = len(teams) - (len(teams) % 3)
    divider = max_working / 3.0
    for idx, team in enumerate(teams):
        team_data = {"name": team.name,
                     "confirmed": team.confirmed,
                     "email": team.email,
                     "members": [member.name for member in team.members],
                     "address": team.location.street,
                     "color": _color_map[int(floor(idx / divider))]}
        location = {"lat": team.location.lat,
                    "lon": team.location.lon}
        data.append({"location": location,
                     "data": team_data})

    return json.dumps(data)