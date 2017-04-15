import hmac
from datetime import timedelta, datetime
from functools import wraps
from hashlib import sha1

from flask import session, redirect, url_for, request, current_app

ADMIN = "valid_admin"
TIME_FORMAT = '%Y%m%d%H%M%S'
TIME_LIMIT = timedelta(hours=3)


def _create_hmac(payload):
    key = current_app.config["SECRET_KEY"]
    payload = payload.encode("utf8")
    mac = hmac.new(key, payload, sha1)
    return mac.hexdigest()


def set_token():
    expire = datetime.now() + TIME_LIMIT
    token = expire.strftime(TIME_FORMAT)
    session[ADMIN] = "%s|%s" % (token, _create_hmac(token))


def delete_token():
    del session[ADMIN]


def _valid_token(token):
    try:
        token, token_mac = token.split(u"|", 1)
    except:
        return False
    if not token_mac == _create_hmac(token):
        return False
    if datetime.now().strftime(TIME_FORMAT) < token:
        return True


def valid_admin(fn):
    @wraps(fn)
    def nufun(*args, **kwargs):
        if ADMIN in session:
            if _valid_token(session[ADMIN]):
                set_token()
                return fn(*args, **kwargs)
            delete_token()
        session["next"] = request.script_root + request.path
        return redirect(url_for(".login"))

    return nufun












