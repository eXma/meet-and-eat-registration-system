import json
import random
from collections import defaultdict
from flask import current_app, session, redirect, url_for, render_template, Blueprint, abort, request
from sqlalchemy import func
import database as db
from database.model import Team, Members, RoundAssignment
from planning.rounds import round_data, assign_default_rounds
from webapp.admin.login import delete_token, set_token, valid_admin
from webapp.forms import AdminLoginForm, ConfirmForm, TeamEditForm

bp = Blueprint('admin', __name__)


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if current_app.config["ADMIN_USER"] == form.login.data and \
                        current_app.config["ADMIN_PASSWORD"] == form.password.data:
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


class _Group(object):
    def __init__(self, idx, name, color):
        self.color = color
        self.name = name
        self.idx = idx
        self._count = 0


def _build_groups(with_na=True):
    groups = [_Group(idx=idx,
                     name=str(idx),
                     color=_group_color(idx))
              for idx in range(1, current_app.config["TEAM_GROUPS"] + 1)]
    if with_na:
        groups.append(_Group(idx=0, name="n/a", color="gray"))

    return groups


@bp.route("/groups")
@valid_admin
def group_map():
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id).all()
    max_working = len(teams) - (len(teams) % 3)
    teams = teams[:max_working]

    groups = _build_groups()

    counts = dict(db.session.query(Team.groups.label("group"),
                                   func.count(Team.id).label("count")
                                   ).group_by(
        Team.groups
    ).filter_by(deleted=False,
                confirmed=True,
                backup=False).all())
    for entry in groups:
        entry.count = counts.get(entry.idx, 0)

    return render_template("admin/groups.html", teams=teams, groups=groups)


class _Round(object):
    def __init__(self, idx, name, short):
        self.idx = idx
        self.name = name
        self.short = short
        self.count = 0


_round_names = [("Vorspeise", 3),
                ("Hauptspeise", 5),
                ("Nach", 4),
                ("n/a", 3)]


def _build_rounds():
    return [_Round(idx, name, name[:n])
            for idx, (name, n)
            in enumerate(_round_names)]


def _team_data(team, color, round_idx):
    team_data = {"name": team.name,
                 "id": team.id,
                 "confirmed": team.confirmed,
                 "email": team.email,
                 "members": [member.name for member in team.members],
                 "address": team.location.street,
                 "color": color,
                 "round": round_idx}

    location = {"lat": team.location.lat,
                "lon": team.location.lon}
    return {"location": location,
            "data": team_data}


@bp.route("/rounds/", defaults={"selected_group": None})
@bp.route("/rounds/<int:selected_group>")
@valid_admin
def round_map(selected_group=None):
    groups = _build_groups(with_na=False)

    if selected_group is None or selected_group not in [g.idx for g in groups]:
        selected_group = groups[0].idx

    rounds = _build_rounds()

    teams = db.session.query(Team) \
        .filter_by(deleted=False,
                   confirmed=True,
                   backup=False,
                   groups=selected_group) \
        .outerjoin(RoundAssignment) \
        .order_by(Team.id).all()

    _update_round_counts(teams, rounds)

    return render_template("admin/rounds.html",
                           teams=[(t, t.round.round) if t.round is not None else
                                  (t, rounds[-1].idx) for t in teams],
                           rounds=rounds,
                           groups=groups,
                           selected_group=selected_group)


def _check_group(selected_group):
    groups = _build_groups(with_na=False)

    if selected_group not in [g.idx for g in groups]:
        abort(404)


def _update_round_counts(teams, rounds):
    round_count = defaultdict(int)
    for team in teams:
        if team.round is not None:
            round_count[team.round.round] += 1
        else:
            round_count[rounds[-1].idx] += 1

    for rnd in rounds:
        rnd.count = round_count[rnd.idx]


@bp.route("/rounds/<int:selected_group>/balanced")
@valid_admin
def balanced_group_rounds(selected_group):
    _check_group(selected_group)

    rounds = _build_rounds()

    teams = db.session.query(Team) \
        .filter_by(deleted=False,
                   confirmed=True,
                   backup=False,
                   groups=selected_group) \
        .outerjoin(RoundAssignment) \
        .order_by(Team.id).all()

    _update_round_counts(teams, rounds)

    balanced = None
    if len(teams) != sum([rnd.count for rnd in rounds[:-1]]):
        balanced = u"Noch nicht alles zugewiesen!"
    elif not all([rnd.count % 3 == 0 for rnd in rounds[:-1]]):
        balanced = u"Nicht alle Zuweisungen durch drei teilbar"
    elif not all(rnd.count == rounds[0].count for rnd in rounds[:-1]):
        balanced = u"G&auml;nge haben unterschiedliche Teilnehmerzahlen"

    return json.dumps(dict(ok=balanced is None, message=balanced))


@bp.route("/rounds/reassign", methods=["POST"])
@valid_admin
def reassign_group():
    if "selected_group" not in request.form:
        abort(400)
    selected_group = int(request.form["selected_group"])
    _check_group(selected_group)

    teams = db.session.query(Team) \
        .filter_by(deleted=False,
                   confirmed=True,
                   backup=False,
                   groups=selected_group).all()

    assign_default_rounds(teams)

    return redirect(url_for(".round_map", selected_group=selected_group))


_color_map = ["blue", "yellow", "green", "red", "gray", "transparent"]


def _colored_teams(group_id):
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False,
                                             groups=group_id).order_by(Team.id).all()

    data = []
    for (team, round_idx) in round_data(teams):
        data.append(_team_data(team, _color_map[round_idx], round_idx))

    return data


def _fix_locations(data):
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
            data.append(_team_data(team, _color_map[4], 4))

    data = _fix_locations(data)

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

    for team in teams:
        data.append(_team_data(team, _group_color(team.groups), 0))

    data = _fix_locations(data)

    return json.dumps(data)


@bp.route("/round_map_teams/<int:selected_group>")
@valid_admin
def round_map_teams(selected_group):
    groups = _build_groups(with_na=False)
    if selected_group not in [g.idx for g in groups]:
        abort(404)

    data = _colored_teams(selected_group)
    data = _fix_locations(data)
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
                                   ).group_by(
        Team.groups
    ).filter_by(deleted=False,
                confirmed=True,
                backup=False).all())
    for idx in range(0, current_app.config["TEAM_GROUPS"] + 1):
        if idx not in counts:
            counts[idx] = 0

    return json.dumps(dict(color=_group_color(group),
                           counts=counts))


@bp.route("/round_update", methods=["POST"])
@valid_admin
def update_round():
    if "round_id" not in request.form or "team_id" not in request.form:
        abort(400)

    rounds = _build_rounds()
    round_id = int(request.form["round_id"])
    team_id = int(request.form["team_id"])

    if round_id not in [rnd.idx for rnd in rounds]:
        abort(400)

    team = db.session.query(Team) \
        .filter_by(id=team_id) \
        .outerjoin(RoundAssignment) \
        .first()

    if team is None:
        abort(404)

    if team.round is not None:
        team.round.round = round_id
    else:
        item = RoundAssignment(team=team, round=round_id)
        db.session.add(item)

    db.session.commit()

    teams = db.session.query(Team) \
        .filter_by(deleted=False,
                   confirmed=True,
                   backup=False,
                   groups=team.groups) \
        .outerjoin(RoundAssignment) \
        .order_by(Team.id).all()

    _update_round_counts(teams, rounds)
    counts = dict([(rnd.idx, rnd.count) for rnd in rounds])

    return json.dumps(dict(counts=counts, color=_color_map[round_id]))


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
