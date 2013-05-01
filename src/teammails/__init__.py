from contextlib import contextmanager
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
            i+=1
        print "Mails sent: %d" % i

