from datetime import datetime
from flask import Blueprint, render_template, request, abort, current_app, redirect, url_for
from flask.ext.mail import Message
from sqlalchemy import func
from forms import TeamRegisterForm
from database.model import Team, Location, Members
import database as db
import json
import tasks


bp = Blueprint('register', __name__)


def _is_soft_end():
    return current_app.config["REGISTER_END"] < datetime.now()


def _is_full():
    teams_qry = db.session.query(func.count(Team.id).label("num")).filter_by(deleted=False).first()
    return current_app.config["MAX_TEAMS"] <= teams_qry.num


def _is_backup():
    return _is_soft_end() or _is_full()


def _is_hard_end():
    return current_app.config["EVENT_DATE"] < datetime.now()


def _do_register(form):
    """Actually perform the registration request

    :type form: TeamRegisterForm
    :param form: The form we've got from the user
    :return: Dont know yet
    """
    if not form.validate_on_submit():
        return None

    team = Team(name=form.teamname.data,
                allergies=form.allergies.data,
                vegetarians=form.vegetarians.data,
                phone=form.phone.data,
                email=form.email.data,
                want_information=form.want_information.data,
                backup=_is_backup())
    db.session.add(team)

    for member_name in (form.member1.data, form.member2.data, form.member3.data):
        member = Members(name=member_name, team=team)
        db.session.add(member)

    location = Location(street=u"%s %s" % (form.street.data, form.streetnumber.data),
                        zip_no=form.zipno.data,
                        extra=form.address_info.data,
                        lat=form.lat.data,
                        lon=form.lon.data,
                        team=team)
    db.session.add(location)
    db.session.commit()

    # ToDo rewrite the message text!
    message_template = "register/confirm_email.txt"
    if team.backup:
        message_template = "register/confirm_email_backup.txt"
    message = Message(current_app.config["CONFIRM_SUBJECT"],
                      recipients=[form.email.data],
                      bcc=[current_app.config["MAIL_DEFAULT_SENDER"]],
                      body=render_template(message_template,
                                           team=team,
                                           token=team.token))
    tasks.get_aqua_distance.spool(team_id=str(team.id))
    current_app.mail.send(message)
    return team


@bp.route('/', methods=("GET",))
def form():
    if _is_hard_end():
        return redirect(url_for(".late"))

    form = TeamRegisterForm()
    if form.validate_on_submit():
        abort(400)

    return render_template('register/index.html', form=form,
                           backup=_is_backup() and not _is_soft_end(),
                           soft_end=_is_soft_end())


@bp.route('/doit', methods=("POST",))
def register_async():
    if _is_hard_end():
        return json.dumps({"state": "error", "errors": "too late"})

    if not request.is_xhr:
        abort(400)

    form = TeamRegisterForm()
    if not form.validate_on_submit():
        return json.dumps({"state": "error", "errors": form.errors})

    if not form.legal_accepted.data:
        return json.dumps({"state": "error", "errors": "terms not confirmed"})

    team = _do_register(form)
    return json.dumps({"state": "success"})


@bp.route("/confirm/<token>")
def confirm(token):
    team = db.session.query(Team).filter_by(token=token).first()
    if team is None:
        abort(401)

    if not team.confirmed:
        team.confirmed = True
        db.session.commit()

    return render_template("register/confirmed.html",
                           team=team,
                           pretty_date=current_app.config["EVENT_DATE_PRETTY"])


@bp.route("/terms")
def terms():
    return render_template("register/terms.html",
                           event_date=current_app.config["EVENT_DATE_PRETTY_LONG"])


@bp.route("/late")
def late():
    if not _is_hard_end():
        return redirect(url_for(".form"))
    return render_template("register/end.html")
