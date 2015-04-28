import json
import random
from math import floor
from flask import current_app, session, redirect, url_for, render_template, Blueprint, abort, request
from sqlalchemy import func
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
    teams = db.session.query(Team).filter_by(deleted=False).order_by(Team.backup, Team.name)
    return render_template("admin/overview.html", teams=teams)


@bp.route("/map")
@valid_admin
def team_map():
    return render_template("admin/map.html")


_group_colors = ["gray", "blue", "yellow", "green"]
def _group_color(group):
    if group is None:
        return "gray"
    else:
        return _group_colors[group % len(_group_colors)]

@bp.route("/groups")
@valid_admin
def group_map():
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id).all()
    max_working = len(teams) - (len(teams) % 3)
    teams = teams[:max_working]

    groups = [dict(idx=idx,
                   name=str(idx),
                   color=_group_color(idx))
              for idx in range(1, current_app.config["TEAM_GROUPS"] + 1)]
    groups.append(dict(idx=0, name="n/a", color="gray"))

    counts = dict(db.session.query(Team.groups.label("group"),
                                   func.count(Team.id).label("count")
                                   ).group_by(Team.groups).all())
    for entry in groups:
        entry["count"] = counts.get(entry["idx"], 0)

    return render_template("admin/groups.html", teams=teams, groups=groups)

_color_map = ["blue", "yellow", "green", "red", "gray", "transparent"]

def _distance_sort(a, b):
    if a.location.center_distance > b.location.center_distance:
        return -1
    if a.location.center_distance < b.location.center_distance:
        return 1
    return 0

def _colored_teams(group_id):
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False,
                                             groups=group_id).order_by(Team.id).all()

    max_working = len(teams) - (len(teams) % 3)
    divider = max_working / 3.0

    working = teams[:max_working]
    teams = sorted(working, _distance_sort) + teams[max_working:]

    data = []
    for idx, team in enumerate(teams):
        color_idx = 0
        if (divider > 0):
            color_idx = min(int(floor(idx / divider)), 3)
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

    return data


@bp.route("/map_teams")
@valid_admin
def map_teams():
    backup = db.session.query(Team).filter_by(deleted=False,
                                              confirmed=True,
                                              backup=True).order_by(Team.id).all()
    unconfirmed = db.session.query(Team).filter_by(deleted=False,
                                                   confirmed=False).order_by(Team.id).all()
    data = []

    for group in range(0, current_app.config["TEAM_GROUPS"] + 1):
        data.extend(_colored_teams(group))

    for idx, collection in [(4, backup), (5, unconfirmed)]:
        for team in collection:
            team_data = {"name": team.name,
                         "id": team.id,
                         "confirmed": team.confirmed,
                         "email": team.email,
                         "members": [member.name for member in team.members],
                         "address": team.location.street,
                         "color": _color_map[4]}

            location = {"lat": team.location.lat,
                        "lon": team.location.lon}
            data.append({"location": location,
                         "data": team_data})

    locations = set()
    for entry in data:
        lat = entry["location"]["lat"]
        lon = entry["location"]["lon"]
        key = "%s|%s" % (lat, lon)

        while key in locations:
            rand = (random.random() - 0.5) * 2
            if rand < 0:
                rand = min(rand, -0.2)
            else:
                rand = max(rand, 0.2)
            lon += rand * 0.0002
            key = "%s|%s" % (lat, lon)

        entry["location"]["lon"] = lon
        locations.add(key)

    return json.dumps(data)


@bp.route("/group_map_teams")
@valid_admin
def group_map_teams():
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id).all()
    data = []

    max_working = len(teams) - (len(teams) % 3)
    teams = teams[:max_working]

    locations = set()
    for team in teams:
        team_data = {"name": team.name,
                     "id": team.id,
                     "confirmed": team.confirmed,
                     "email": team.email,
                     "members": [member.name for member in team.members],
                     "address": team.location.street,
                     "color": _group_color(team.groups)}

        lat = team.location.lat
        lon = team.location.lon
        while "%s|%s" % (lat, lon) in locations:
            rand = (random.random() - 0.5) * 2
            if rand < 0:
                rand = min(rand, -0.2)
            else:
                rand = max(rand, 0.2)
            lon += rand * 0.0002
        locations.add("%s|%s" % (lat, lon))

        location = {"lat": lat,
                    "lon": lon}
        data.append({"location": location,
                     "data": team_data})

    return json.dumps(data)


@bp.route("/group_update", methods=["POST"])
@valid_admin
def update_group():
    team_id = int(request.form["team_id"])
    team = db.session.query(Team).filter_by(id=team_id).first()
    if team is None:
        abort(404)

    group = int(request.form["group_id"])
    if group not in range(0, current_app.config["TEAM_GROUPS"] + 1):
        abort(400)

    team.groups = group
    db.session.commit()

    counts = dict(db.session.query(Team.groups.label("group"),
                                   func.count(Team.id).label("count")
                                   ).group_by(Team.groups).all())
    for idx in range(0, current_app.config["TEAM_GROUPS"] + 1):
        if idx not in counts:
            counts[idx] = 0

    return json.dumps(dict(color=_group_color(group),
                           counts=counts))



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
        form.vegetarians.data = team.vegetarians
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
