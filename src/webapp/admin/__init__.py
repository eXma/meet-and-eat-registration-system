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
    teams = db.session.query(Team).order_by(Team.name)
    return render_template("admin/overview.html", teams=teams)


@bp.route("/map")
@valid_admin
def team_map():
    return render_template("admin/map.html")


_color_map = ["blue", "yellow", "green", "red"]


@bp.route("/map_teams")
@valid_admin
def map_teams():
    teams = db.session.query(Team).filter_by(confirmed=True).order_by(Team.id).all()
    data = []

    max_working = len(teams) - (len(teams) % 3)
    divider = max_working / 3.0

    def distance_sort(a, b):
        if a.location.center_distance > b.location.center_distance:
            return -1
        if a.location.center_distance < b.location.center_distance:
            return 1
        return 0

    working = teams[:max_working]
    teams = sorted(working, distance_sort) + teams[max_working:]

    for idx, team in enumerate(teams):
        color_idx = 0
        if (divider > 0):
            color_idx = int(floor(idx / divider))
        team_data = {"name": team.name,
                     "confirmed": team.confirmed,
                     "email": team.email,
                     "members": [member.name for member in team.members],
                     "address": team.location.street,
                     "color": _color_map[color_idx]}
        location = {"lat": team.location.lat,
                    "lon": team.location.lon}
        data.append({"location": location,
                     "data": team_data})

    return json.dumps(data)