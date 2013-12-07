#!env python

import database as db
from database.model import Team, RouteDistance
from geotools import simple_distance
from geotools.routing import MapPoint
from webapp.cfg.config import DB_CONNECTION

print "init db..."
db.init_session(connection_string=DB_CONNECTION)

print "fetch teams..."
teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True).all()

distances = []

print "fetch distances..."
for (idx, team_from) in enumerate(teams):
    location_from = MapPoint.from_team(team_from)
    for team_to in teams[(idx + 1):]:
        route_a = db.session.query(RouteDistance).filter_by(
            location_from=team_from.location, location_to=team_to.location).first()
        route_b = db.session.query(RouteDistance).filter_by(
            location_to=team_from.location, location_from=team_to.location).first()

        if (route_a is not None) and (route_b is not None):
            continue

        location_to = MapPoint.from_team(team_to)

        dist = int(simple_distance(location_from, location_to) * 1000)
        log = u"%s -> %s :: %d" % (team_from.name, team_to.name, dist)
        print log.encode("utf8")

        if route_a is None:
            distances.append(RouteDistance(location_from=team_from.location, location_to=team_to.location, distance=dist))
        if route_b is None:
            distances.append(RouteDistance(location_to=team_from.location, location_from=team_to.location, distance=dist))

print "write to db..."
db.session.add_all(distances)
db.session.commit()
