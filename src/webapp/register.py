from flask import Blueprint, render_template, request, abort
from forms import TeamRegisterForm
from database.model import Team, Location, Members
from database import session
import hashlib
import datetime
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

    token_hash = hashlib.sha1()
    token_hash.update(form.name)
    token_hash.update(str(datetime.datetime.now()))

    team = Team(name=form.name,
                allergies=form.allergies,
                vegetarians=form.vegetarians,
                token=token_hash.hexdigest())
    session.add(team)

    for member_name in (form.member1, form.member2, form.member3):
        member = Members(name=member_name, team=team)
        session.add(member)

    location = Location(street=form.address,
                        zip_no=form.zipno,
                        extra=form.address_info,
                        lat=form.lat,
                        lon=form.lon)
    session.add(location)
    session.commit()
    # TODO: send mail

    return team


@bp.route('/', methods=("GET", "POST"))
def form():
    form = TeamRegisterForm()
    if form.validate_on_submit():
        team = _do_register(form)
        return "Submitted: %s -> %s" % (form, team)
    return render_template('register/form.html', form=form)


@bp.route('/doit', methods=("POST",))
def register_async():
    if not request.is_xhr:
        abort(400)

    form = TeamRegisterForm()
    if not form.validate_on_submit():
        return json.dumps({"state": "error", "cause": "go away"})

    team = _do_register(form)
    return json.dumps({"state": "success", "token": team.token})


@bp.route("/confirm/<token>")
def confirm(token):
    team = session.query(Team).filter_by(token=token).first()
    if team is None:
        abort(401)

    team.confirmed = True
    session.commit()

    return render_template("register/confirmed.html", team=team)