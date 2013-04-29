import json
import sys
import database as db
from database.model import Team
from geotools import simple_distance
from geotools.routing import MapPoint
from webapp.cfg.config import DB_CONNECTION


if len(sys.argv) == 2:
    MAX_TEAMS = sys.argv[1]
else:
    MAX_TEAMS = 9

print "init db..."
db.init_session(connection_string=DB_CONNECTION)

print "fetch teams..."

teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True).order_by(Team.id).limit(
    MAX_TEAMS).all()

distances = list()

print "fetch distances..."

for (idx, team_from) in enumerate(teams):
    location_from = MapPoint.from_team(team_from)
    for team_to in teams[idx + 1]:
        location_to = MapPoint.from_team(team_to)

        dist = int(simple_distance(location_from, location_to) * 1000)
        distances.append({"src": str(team_from.id), "dst": str(team_to.id), "value": dist, "text": str(dist)})
        distances.append({"src": str(team_to.id), "dst": str(team_from.id), "value": dist, "text": str(dist)})

print "write distance data..."
with open("distances.json", "w+") as f:
    json.dump(distances, f)
