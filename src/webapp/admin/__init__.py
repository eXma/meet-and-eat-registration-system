import json
from math import floor
from flask import current_app, session, redirect, url_for, render_template, Blueprint, abort
from database.model import Team, Members
from webapp.admin.login import delete_token, set_token, valid_admin
from webapp.forms import AdminLoginForm, ConfirmForm, TeamEditForm

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
    teams = db.session.query(Team).filter_by(deleted=False).order_by(Team.name)
    return render_template("admin/overview.html", teams=teams)


@bp.route("/map")
@valid_admin
def team_map():
    return render_template("admin/map.html")


_color_map = ["blue", "yellow", "green", "red", "gray"]


@bp.route("/map_teams")
@valid_admin
def map_teams():
    teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=False).order_by(Team.id).all()
    backup = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=True).order_by(Team.id).all()
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
    teams = sorted(working, distance_sort) + teams[max_working:] + backup

    for idx, team in enumerate(teams):
        color_idx = 0
        if (divider > 0):
            color_idx = min(int(floor(idx / divider)), 3)
        if team.backup:
            color_idx = 4
        team_data = {"name": team.name,
                     "id": team.id,
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


@bp.route("/edit/<int:team_id>", methods=["GET", "POST"])
def edit_team(team_id):
    team = db.session.query(Team).filter_by(id=team_id).first()
    if team is None:
        abort(404)

    form = TeamEditForm()

    if form.validate_on_submit():
        team.name = form.name.data
        team.email = form.email.data
        team.phone = form.phone.data
        team.location.street = form.address.data
        team.location.extra = form.address_info.data
        team.location.zipno = form.zipno.data
        team.location.lat = form.lat.data
        team.location.lon = form.lon.data
        team.allergies = form.allergies.data
        team.vegetarians = form.vegetarians.data
        team.backup = form.backup.data

        for idx, member in enumerate([form.member1, form.member2, form.member3]):
            if len(team.members) > idx:
                team.members[idx].name = member.data
            else:
                db.session.add(Members(name=member.data,
                                       team=team))
        db.session.commit()

        # todo: flash something
        return redirect(url_for(".overview"))

    if not form.is_submitted():
        form.name.data = team.name
        form.email.data = team.email
        form.phone.data = team.phone
        form.address.data = team.location.street
        form.address_info.data = team.location.extra
        form.zipno.data = team.location.zip_no
        form.lat.data = team.location.lat
        form.lon.data = team.location.lon
        for idx, member in enumerate([form.member1, form.member2, form.member3]):
            if len(team.members) > idx:
                member.data = team.members[idx].name
        form.allergies.data = team.allergies
        form.vegetarians.data = team.allergies
        form.backup.data = team.backup

    # ToDo make lat/lon selectable via a map!
    return render_template("admin/team_edit.html", form=form, team=team)


@bp.route("/delete/<int:team_id>", methods=["GET", "POST"])
def delete_team(team_id):
    team = db.session.query(Team).filter_by(id=team_id).first()
    if team is None:
        abort(404)

    form = ConfirmForm()
    if form.validate_on_submit():
        if form.confirmed.data is True:
            team.deleted = True
            db.session.commit()
            return redirect(url_for(".overview"))

    return render_template("admin/confirmation.html",
                           what=u"Loeschen von Team %d: '%s'" % (team.id, team.name),
                           cancel_target=url_for(".overview"),
                           form=form)
