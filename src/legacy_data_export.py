import json
import sys

import database as db
from database.model import Team
from geotools import simple_distance
from geotools.routing import MapPoint
from cfg import config

import argparse
import cfg


arguments = argparse.ArgumentParser()
arguments.add_argument("-c", "--config", help="set the configfile",
                       default="config.yaml")

arguments.add_argument("max_teams", help="Max. number of teams to export")

args = arguments.parse_args()
cfg.load_config(args.config)

MAX_TEAMS = args.max_teams

print "init db..."
db.init_session(connection_string=config.DB_CONNECTION)

print "fetch teams..."

teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True).filter_by(backup=False).order_by(
    Team.id).limit(MAX_TEAMS).all()

distances = list()

print "fetch distances..."

for (idx, team_from) in enumerate(teams):
    location_from = MapPoint.from_team(team_from)
    for team_to in teams[(idx + 1):]:
        location_to = MapPoint.from_team(team_to)

        dist = int(simple_distance(location_from, location_to) * 1000)
        distances.append({"src": str(team_from.id), "dst": str(team_to.id), "value": dist, "text": str(dist)})
        distances.append({"src": str(team_to.id), "dst": str(team_from.id), "value": dist, "text": str(dist)})

print "write distance data..."
with open("legacy_distances.json", "w+") as f:
    json.dump(distances, f)
