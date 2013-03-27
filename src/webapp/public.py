import json
from flask import Blueprint, render_template

import database as db
from database.model import Team

bp = Blueprint('public', __name__)


@bp.route("/map")
def map_page():
    return render_template("public/map.html")


@bp.route("/map_teams")
def map_teams():
    qry = db.session.query(Team).filter_by(confirmed=True).filter_by(deleted=False)
    data = []
    for item in qry:
        if item.location is not None:
            data.append({"lat": item.location.lat,
                         "lon": item.location.lon})
    return json.dumps(data)