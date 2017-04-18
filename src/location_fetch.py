#!/usr/bin/env python

import argparse
import time

import database as db
from cfg import config
import cfg
from database.model import Team, RouteDistance
from geotools import routing
from geotools.routing import MapPoint


def fetch_dist():
    pass


arguments = argparse.ArgumentParser()
arguments.add_argument("-c", "--config", help="set the configfile",
                       default="config.yaml")

arguments.add_argument("max_teams", help="Max. number of teams to export")

args = arguments.parse_args()

print "load cfg..."
cfg.load_config(args.config)

print "init db..."
db.init_session(connection_string=config.DB_CONNECTION)

print "fetch teams..."
teams = db.session.query(Team).filter_by(deleted=False) \
    .filter_by(confirmed=True) \
    .order_by(Team.name).all()

distances = []

print "fetch distances..."
for (idx, team_from) in enumerate(teams):
    location_from = MapPoint.from_team(team_from)
    dest_teams = set(teams[(idx + 1):])
    while len(dest_teams):
        try:
            with routing.Router() as router:
                for team_to in list(dest_teams):
                    route_a = db.session.query(RouteDistance).filter_by(
                        location_from=team_from.location,
                        location_to=team_to.location).first()
                    route_b = db.session.query(RouteDistance).filter_by(
                        location_to=team_from.location,
                        location_from=team_to.location).first()

                    if (route_a is not None) and (route_b is not None):
                        dest_teams.remove(team_to)
                        continue

                    location_to = MapPoint.from_team(team_to)

                    dist = int(router.route(location_from, location_to).distance * 1000)
                    log = u"%s -> %s :: %d" % (team_from.name, team_to.name, dist)
                    print log.encode("utf8")

                    if route_a is None:
                        distances.append(RouteDistance(location_from=team_from.location,
                                                       location_to=team_to.location,
                                                       distance=dist))
                    if route_b is None:
                        distances.append(RouteDistance(location_to=team_from.location,
                                                       location_from=team_to.location,
                                                       distance=dist))
                    dest_teams.remove(team_to)
            db.session.add_all(distances)
            db.session.commit()
            distances = []
        except Exception as e:
            print e
            time.sleep(30)
