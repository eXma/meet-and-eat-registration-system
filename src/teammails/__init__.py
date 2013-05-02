from collections import defaultdict
from contextlib import contextmanager
from email.header import make_header
import os
import smtplib
import database as db

from email.mime.text import MIMEText

from jinja2 import Template
from database.model import Team

from webapp.cfg import config


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


def get_template(name):
    filename = "%s.txt" % name
    filepath = os.path.join(os.path.dirname(__file__), "templates", filename)
    if not os.path.isfile(filepath):
        raise Exception("File not found: %s!" % filepath)

    with open(filepath, "r") as fn:
        return Template(unicode(fn.read(), "utf8"))


def informal_to_teams(template_name, subject, debug=True):
    template = get_template(template_name)
    sender = "meet&eat Orga <%s>" % config.MAIL_DEFAULT_SENDER
    envelope = config.MAIL_DEFAULT_SENDER

    print "connect to SMTP...."
    with smtp_session() as session:
        print "Send Mails..."
        i = 0
        for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True):
            content = template.render(name=team.name)
            msg = MIMEText(content, "plain", "utf8")

            rcpt = team.email
            if debug:
                rcpt = config.MAIL_DEFAULT_SENDER

            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = rcpt

            session.sendmail(envelope, [rcpt] + ["redaktion@exmatrikulationsamt.de"], msg.as_string())
            i += 1
        print "Mails sent: %d" % i


def plans_to_teams(plan_results, debug=True):
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
  (Vegeratier dabei: %(vegetarians)s)
  Telefon: %(guestphone)s
"""
    subject = "Meet&Eat - Abendplanung Team %s"
    round_datas = ({"time": "18:00", "name": "Vorspeise"},
                   {"time": "19:30", "name": "Hauptgericht"},
                   {"time": "21:00", "name": "Dessert"})

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
    for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True):
        teams[str(team.id)] = team

    i = 0
    print "Connect to smtp..."
    with smtp_session() as session:
        print "Send mails..."
        for team in plan_results:
            plan_detail = []
            for (round_idx, host) in enumerate(plan_results[team]):
                round_data = round_datas[round_idx]
                if team != host:
                    detail = guestentry % {"time": round_data["time"],
                                           "roundname": round_data["name"],
                                           "host": teams[host].name,
                                           "address": teams[host].location.street,
                                           "bell": teams[host].location.extra,
                                           "phone": teams[host].phone,
                                           "link": "WURSt"}
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
            text = template.render(eventdate=config.EVENT_DATE, teamname=teams[team].name, plan=plan)

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
