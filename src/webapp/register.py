from flask import Blueprint, render_template, request, abort, current_app
from flask.ext.mail import Message
from forms import TeamRegisterForm
from database.model import Team, Location, Members
import database as db
import json


bp = Blueprint('register', __name__)


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
                email=form.email.data)
    db.session.add(team)

    for member_name in (form.member1.data, form.member2.data, form.member3.data):
        member = Members(name=member_name, team=team)
        db.session.add(member)

    location = Location(street=form.street.data,
                        zip_no=form.zipno.data,
                        extra=form.address_info.data,
                        lat=form.lat.data,
                        lon=form.lon.data,
                        team=team)
    db.session.add(location)
    db.session.commit()

    # ToDo rewrite the message text!
    message = Message(current_app.config["CONFIRM_SUBJECT"],
                      recipients=[form.email.data],
                      bcc=[current_app.config["DEFAULT_MAIL_SENDER"]],
                      body=render_template("register/confirm_email.txt",
                                           teamname=team.name,
                                           token=team.token))
    current_app.mail.send(message)
    return team


@bp.route('/', methods=("GET", "POST"))
def form():
    form = TeamRegisterForm()
    if form.validate_on_submit():
        team = _do_register(form)
        return "Submitted"
    return render_template('register/index.html', form=form)


@bp.route('/doit', methods=("POST",))
def register_async():
    if not request.is_xhr:
        abort(400)

    form = TeamRegisterForm()
    if not form.validate_on_submit():
        return json.dumps({"state": "error", "errors": form.errors})

    team = _do_register(form)
    return json.dumps({"state": "success"})


@bp.route("/confirm/<token>")
def confirm(token):
    team = db.session.query(Team).filter_by(token=token).first()
    if team is None:
        abort(401)

    team.confirmed = True
    db.session.commit()

    return render_template("register/confirmed.html", team=team)