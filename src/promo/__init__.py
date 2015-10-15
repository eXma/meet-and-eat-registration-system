from contextlib import contextmanager
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from cfg import config, parse_end_date

import os
import re

from teammails import base_path, get_template, smtp_session


def address_set(filename):
    if not os.path.isfile(filename):
        raise Exception("File not found: %s!" % filename)

    splitter = re.compile(r"\s*[,; ]\s*")
    with open(filename, "r") as fn:
        return set([addr for part in
                    (splitter.split(line.strip()) for line in fn)
                    for addr in part])


def send_spam(address_file, debug=True):
    template = get_template("spammail", path=base_path(__file__))
    sender = "meet&eat Orga <%s>" % config.MAIL_DEFAULT_SENDER
    envelope = config.MAIL_DEFAULT_SENDER

    register_end = parse_end_date(config.REGISTER_END)

    data = dict(event_date=config.EVENT_DATE,
                volume=config.VOLUME,
                register_end_date=register_end.strftime("%d.%m.%Y"),
                pretty_event_date=config.EVENT_DATE_PRETTY,
                address=None)

    subject = "Einladung zum %d. meet&eat am %s" % (config.VOLUME, config.EVENT_DATE_PRETTY)

    with smtp_session() as session:
        print "Send Mails ",

        i = 0
        for address in address_set(address_file):
            i += 1
            data["address"] = address
            content = template.render(**data)

            recpt = address
            if debug:
                recpt = envelope

            msg = MIMEText(content, "plain", "utf8")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recpt
            msg["Date"] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid("promo-%d" % i)

            session.sendmail(envelope, [recpt], msg.as_string())
            print ".",

        print " Done - %d Mails sent" % i
