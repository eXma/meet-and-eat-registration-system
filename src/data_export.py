#!/usr/bin/env python

import argparse
import json
from argparse import ArgumentParser
from collections import defaultdict

from sqlalchemy import not_

import database as db
import cfg
from cfg import config
from database.model import Team, RouteDistance
from geotools import simple_distance
from geotools.routing import MapPoint
from planning.rounds import round_data


def get_round_distances(from_teams, to_teams):
    # ToDo use cached values!
    distances = defaultdict(dict)
    for team_from in from_teams:
        location_from = MapPoint.from_team(team_from)
        for team_to in to_teams:
            route = db.session.query(RouteDistance).filter_by(location_from=team_from.location,
                                                      location_to=team_to).first()
            if route is None:
                location_to = MapPoint.from_team(team_to)
                distances[team_from.id][team_to.id] = simple_distance(location_from, location_to)
            else:
                distances[team_from.id][team_to.id] = route.distance / 1000.0

    return distances


def write_planning_data(teams, filename):
    max_working = len(teams) - (len(teams) % 3)
    print "Working on %d teams for %s" % (max_working, filename)

    data = []
    round_teams = defaultdict(list)

    idx = 0
    for (team, round_idx) in round_data(teams):
        team_data = {"name": team.name,
                     "id": team.id,
                     "idx": idx,
                     "location": {"lat": team.location.lat,
                                  "lon": team.location.lon},
                     "round_host": round_idx}
        round_teams[round_idx].append(team)
        data.append(team_data)
        idx += 1

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
    args.add_argument("-c", "--config", help="set the configfile", default="config.yaml")
    args.add_argument("--name", help="Part of the filenames", required=False, type=str)

    subs = args.add_subparsers()
    informal = subs.add_parser("distance_data", help="Team and distance data for planning algorithms")
    informal.add_argument("-s", "--slice", type=int, metavar="N", help="Slice the teams ro this value", required=False)
    informal.add_argument("-S", "--separate", type=int, metavar="I", nargs=argparse.REMAINDER,
                          help="Separate the given ids to a new group",
                          required=False)
    informal.add_argument("-g", "--group", type=int, metavar="G", required=False,
                          help="Export data for the given group-id")
    informal.set_defaults(func=cmd_distance_data)

    return args.parse_args()


def cmd_distance_data(args):
    print "init db..."
    db.init_session(connection_string=config.DB_CONNECTION)

    print "fetch teams..."
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id)

    if args.group is not None:
        teams = teams.filter_by(groups=args.group)

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
    cfg.load_config(args.config)
    args.func(args)