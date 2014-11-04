#!env python

from argparse import ArgumentParser
import argparse
from collections import defaultdict
import json
from math import floor

from sqlalchemy import not_

from database.model import Team
from geotools import simple_distance
from geotools.routing import MapPoint
from cfg.config import DB_CONNECTION
import database as db


def get_round_distances(from_teams, to_teams):
    # ToDo use cached values!
    distances = defaultdict(dict)
    for team_from in from_teams:
        location_from = MapPoint.from_team(team_from)
        for team_to in to_teams:
            location_to = MapPoint.from_team(team_to)

            distances[team_from.id][team_to.id] = simple_distance(location_from, location_to)
    return distances


def distance_sort(a, b):
    if a.location.center_distance > b.location.center_distance:
        return -1
    if a.location.center_distance < b.location.center_distance:
        return 1
    return 0


def write_planning_data(teams, filename):
    max_working = len(teams) - (len(teams) % 3)
    divider = max_working / 3.0
    print "Working on %d teams for %s" % (max_working, filename)

    data = []
    round_teams = defaultdict(list)

    working = teams[:max_working]
    teams = sorted(working, distance_sort) + teams[max_working:]

    for idx, team in enumerate(teams):
        round_idx = 0
        if divider > 0:
            round_idx = min(int(floor(idx / divider)), 3)
        team_data = {"name": team.name,
                     "id": team.id,
                     "location": {"lat": team.location.lat,
                                  "lon": team.location.lon},
                     "round_host": round_idx}
        round_teams[round_idx].append(team)
        data.append(team_data)

    print "write team data..."

    with open("teams%s.json" % filename, "w+") as f:
        json.dump(data, f)

    distance_data = []
    print "get round 1 to 2 routes..."
    distance_data.append(get_round_distances(round_teams[0], round_teams[1]))

    print "get round 2 to 3 routes..."
    distance_data.append(get_round_distances(round_teams[1], round_teams[2]))

    print "write distance data..."
    with open("distances%s.json" % filename, "w+") as f:
        json.dump(distance_data, f)


def parse_args():
    args = ArgumentParser()
    args.add_argument("--name", help="Part of the filenames", required=False, type=str)

    subs = args.add_subparsers()
    informal = subs.add_parser("distance_data", help="Team and distance data for planning algorithms")
    informal.add_argument("-s", "--slice", type=int, metavar="N", help="Slice the teams ro this value", required=False)
    informal.add_argument("-S", "--separate", type=int, metavar="I", nargs=argparse.REMAINDER,
                          help="Separate the given ids to a new group",
                          required=False)
    informal.set_defaults(func=cmd_distance_data)

    return args.parse_args()


def cmd_distance_data(args):
    print "init db..."
    db.init_session(connection_string=DB_CONNECTION)

    print "fetch teams..."
    teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=False).order_by(Team.id)
    if args.slice is not None:
        teams = teams.limit(args.slice)

    fname = ""
    if args.name is not None:
        fname = "_%s" % args.name

    if args.separate is not None:
        write_planning_data(teams.filter(Team.id.in_(args.separate)).all(), "%s_1" % fname)
        write_planning_data(teams.filter(not_(Team.id.in_(args.separate))).all(), "%s_2" % fname)
    else:
        write_planning_data(teams.all(), fname)

    print "finish!"


if __name__ == "__main__":
    args = parse_args()
    args.func(args)