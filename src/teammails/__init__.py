from collections import defaultdict
from contextlib import contextmanager
from email.utils import formatdate
import os
import smtplib
from email.mime.text import MIMEText

from sqlalchemy import not_
from jinja2 import Template

from cfg import config
import database as db
from database.model import Team
from geotools import openroute_link, gmaps_link
from geotools.routing import MapPoint


@contextmanager
def smtp_session():
    session = smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT)
    if config.MAIL_USERNAME is not None:
        session.starttls()
        session.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)

    try:
        yield session
    finally:
        session.quit()


def base_path(file):
    return os.path.dirname(
        os.path.abspath(
            os.path.expanduser(file)))


def get_template(name, path=None):
    filename = "%s.txt" % name

    if path is None:
        path = base_path(__file__)

    filepath = os.path.join(path, "templates", filename)
    if not os.path.isfile(filepath):
        raise Exception("File not found: %s!" % filepath)

    with open(filepath, "r") as fn:
        return Template(unicode(fn.read(), "utf8"))


def informal_to_teams(template_name, subject, debug=True):
    template = get_template(template_name)
    sender = "meet&eat Orga <%s>" % config.MAIL_DEFAULT_SENDER
    envelope = config.MAIL_DEFAULT_SENDER

    data = dict(
        num_teams=db.session.query(Team).filter_by(deleted=False,
                                                   confirmed=True,
                                                   backup=False).count(),
        volume=config.VOLUME
    )

    print "connect to SMTP...."
    with smtp_session() as session:
        print "Send Mails..."
        i = 0
        for team in db.session.query(Team).filter_by(deleted=False,
                                                     confirmed=True,
                                                     backup=False):
            data["name"] = team.name
            content = template.render(**data)
            msg = MIMEText(content, "plain", "utf8")

            rcpt = team.email
            if debug:
                rcpt = config.MAIL_DEFAULT_SENDER

            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = rcpt
            msg['Date'] = formatdate(localtime=True)

            session.sendmail(envelope, [rcpt] + ["redaktion@exmatrikulationsamt.de"], msg.as_string())
            i += 1
        print "Mails sent: %d" % i


def plans_to_teams(plan_results, debug=True, group=None, include=None, exclude=None):
    guestentry = """
%(time)s Uhr - %(roundname)s bei "%(host)s"
%(address)s
Klingeln bei: %(bell)s
Bei Problemen erreicht ihr dieses Team unter: %(phone)s
Routenlink: %(link)s"""

    hostentry = """
%(time)s Uhr - %(roundname)s wird von Euch zubereitet. (%(teamname)s)

zu Gast sind bei Euch:
%(guests)s"""

    hostguests = """
  Team "%(guestname)s"
  (Allergien: %(allergies)s)
  (Vegetarier dabei: %(vegetarians)s)
  Telefon: %(guestphone)s
"""
    subject = "Meet&Eat - Abendplanung Team %s"
    round_datas = ({"time": "18:00", "name": "Vorspeise"},
                   {"time": "20:00", "name": "Hauptgericht"},
                   {"time": "21:30", "name": "Dessert"})

    print "Preprocess plan..."
    guestmap = defaultdict(list)
    for team in plan_results:
        for host in plan_results[team]:
            if team != host:
                guestmap[host].append(team)

    template = get_template("plan")
    sender = "meet&eat Orga <%s>" % config.MAIL_DEFAULT_SENDER
    envelope = config.MAIL_DEFAULT_SENDER

    print "Fetch data..."
    teams = {}
    qry = db.session.query(Team).filter_by(deleted=False,
                                           confirmed=True,
                                           backup=False)
    if include is not None:
        qry = qry.filter(Team.id.in_(include))
    if exclude is not None:
        qry = qry.filter(not_(Team.id.in_(exclude)))
    if group is not None:
        qry = qry.filter_by(groups=group)
    for team in qry:
        teams[str(team.id)] = team

    i = 0
    print "Connect to smtp..."
    with smtp_session() as session:
        print "Send mails..."
        for team in plan_results:
            plan_detail = []
            start_point = MapPoint.from_team(teams[team])
            for (round_idx, host) in enumerate(plan_results[team]):
                round_data = round_datas[round_idx]
                end_point = MapPoint.from_team(teams[host])
                # route = openroute_link([start_point, end_point])
                route = gmaps_link([start_point, end_point])
                start_point = end_point
                if team != host:
                    detail = guestentry % {"time": round_data["time"],
                                           "roundname": round_data["name"],
                                           "host": teams[host].name,
                                           "address": teams[host].location.street,
                                           "bell": teams[host].location.extra,
                                           "phone": teams[host].phone,
                                           "link": route}
                    plan_detail.append(detail)
                else:
                    guest_details = []
                    for guest in guestmap[team]:
                        guest_detail = hostguests % {"guestname": teams[guest].name,
                                                     "allergies": teams[guest].allergies,
                                                     "vegetarians": teams[guest].vegetarians,
                                                     "guestphone": teams[guest].phone}
                        guest_details.append(guest_detail)
                    detail = hostentry % {"time": round_data["time"],
                                          "roundname": round_data["name"],
                                          "teamname": teams[team].name,
                                          "guests": "\n".join(guest_details)}
                    plan_detail.append(detail)
            plan = "\n\n".join(plan_detail)
            text = template.render(eventdate=config.EVENT_DATE,
                                   teamname=teams[team].name,
                                   volume=config.VOLUME,
                                   contact_email=config.CONTACT_EMAIL,
                                   contact_phone=config.CONTACT_PHONE,
                                   plan=plan)
            msg = MIMEText(text, "plain", "utf8")

            rcpt = teams[team].email
            if debug:
                rcpt = config.MAIL_DEFAULT_SENDER

            msg['Subject'] = subject % teams[team].name
            msg['From'] = sender
            msg['To'] = rcpt

            session.sendmail(envelope, [rcpt] + ["redaktion@exmatrikulationsamt.de"], msg.as_string())
            i += 1
        print "Mails sent: %d" % i


def emergency_plan_routes(plan_results, debug=True):
    sender = "meet&eat Orga <%s>" % config.MAIL_DEFAULT_SENDER
    envelope = config.MAIL_DEFAULT_SENDER

    template = get_template("emergency_routes")
    aqua = MapPoint(51.04485, 13.74011)

    teams = {}
    for team in db.session.query(Team).filter_by(deleted=False,
                                                 confirmed=True,
                                                 backup=False):
        teams[str(team.id)] = team

    i = 0
    with smtp_session() as session:
        for team in plan_results:
            route_data = {}
            plan = plan_results[team]

            if plan[0] == team:
                route_data["pre"] = "braucht ihr keine, da diese ja bei euch stattfindet"
            else:
                # route_data["pre"] = openroute_link(
                #    [MapPoint.from_team(teams[team]), MapPoint.from_team(teams[plan[0]])])
                route_data["pre"] = gmaps_link(
                    [MapPoint.from_team(teams[team]), MapPoint.from_team(teams[plan[0]])])

            for (idx, name) in enumerate(["main", "dessert"]):
                # route_data[name] = openroute_link(
                #    [MapPoint.from_team(teams[plan[idx]]), MapPoint.from_team(teams[plan[idx + 1]])])
                route_data[name] = gmaps_link(
                    [MapPoint.from_team(teams[plan[idx]]), MapPoint.from_team(teams[plan[idx + 1]])])

            # route_data["aqua"] = openroute_link([MapPoint.from_team(teams[plan[2]]), aqua])
            route_data["aqua"] = gmaps_link([MapPoint.from_team(teams[plan[2]]), aqua])

            rcpt = teams[team].email
            if debug:
                rcpt = config.MAIL_DEFAULT_SENDER

            text = template.render(name=teams[team].name, routes=route_data)
            msg = MIMEText(text, "plain", "utf8")
            msg['Subject'] = "Betreff: Korrektur der Routenlinks zum meet&eat"
            msg['From'] = sender
            msg['To'] = rcpt

            session.sendmail(envelope, [rcpt] + ["redaktion@exmatrikulationsamt.de"], msg.as_string())
            i += 1
    print "Mails sent: %d" % i
