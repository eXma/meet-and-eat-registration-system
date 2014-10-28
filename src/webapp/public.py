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
    qry = db.session.query(Team).filter_by(confirmed=True).filter_by(deleted=False).filter_by(backup=False)
    data_dict = {}
    for item in qry:
        if item.location is not None:
            ident = "%s%s" % (item.location.lat, item.location.lon)
            if ident not in data_dict:
                data_dict[ident] = {"lat": item.location.lat,
                                    "lon": item.location.lon,
                                    "name": item.name}
            else:
                data_dict[ident]["name"] += "<br>" + item.name
    data = [entry for entry in data_dict.itervalues()]
    return json.dumps(data)
