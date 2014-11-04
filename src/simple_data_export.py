#!env python


from collections import defaultdict
import json
from math import floor
import sys

import database as db
from database.model import Team
from geotools import simple_distance
from geotools.routing import MapPoint
from cfg.config import DB_CONNECTION


if len(sys.argv) == 2:
    MAX_TEAMS = sys.argv[1]
else:
    MAX_TEAMS = 9


print "init db..."
db.init_session(connection_string=DB_CONNECTION)

print "fetch teams..."

teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=False).order_by(Team.id).limit(MAX_TEAMS).all()
data = []
round_teams = defaultdict(list)

max_working = len(teams) - (len(teams) % 3)
divider = max_working / 3.0

def distance_sort(a, b):
    if a.location.center_distance > b.location.center_distance:
        return -1
    if a.location.center_distance < b.location.center_distance:
        return 1
    return 0

working = teams[:max_working]
teams = sorted(working, distance_sort) + teams[max_working:]

for idx, team in enumerate(teams):
    round_idx = 0
    if (divider > 0):
        round_idx = min(int(floor(idx / divider)), 3)
    team_data = {"name": team.name,
                 "id": team.id,
                 "location": {"lat": team.location.lat,
                              "lon": team.location.lon},
                 "round_host": round_idx}
    round_teams[round_idx].append(team)
    data.append(team_data)

print "write team data..."

with open("teams.json", "w+") as f:
    json.dump(data, f)


def get_round_distances(from_teams, to_teams):
    distances = defaultdict(dict)
    for team_from in from_teams:
        location_from = MapPoint.from_team(team_from)
        for team_to in to_teams:
            location_to = MapPoint.from_team(team_to)

            distances[team_from.id][team_to.id] = simple_distance(location_from, location_to)
    return distances


distance_data = []
print "get round 1 to 2 routes..."
distance_data.append(get_round_distances(round_teams[0], round_teams[1]))

print "get round 2 to 3 routes..."
distance_data.append(get_round_distances(round_teams[1], round_teams[2]))

print "write distance data..."
with open("distances.json", "w+") as f:
    json.dump(distance_data, f)
