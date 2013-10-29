#!env python

from argparse import ArgumentParser
from collections import defaultdict
import json
import imp
from math import floor

import database as db
from database.model import Team, RouteDistance
from geotools import openroute_link
from geotools.routing import MapPoint
from webapp.cfg.config import DB_CONNECTION
from planning.cluster_graph import process_plan


db.init_session(connection_string=DB_CONNECTION)


def read_legacy_plan(in_file):
    with open(in_file, "r") as in_fn:
        data = json.load(in_fn)

    result = {}
    for entry in data:
        result[entry["team_id"][0]] = [station[0] for station in entry["plan"]]
    return result


def read_dan_marc_partial(in_file):
    """Debug output prefixed with "data="

    :param in_file: The file with the result
    :return: The processed data
    """
    contents = imp.load_source("_dummy", in_file)

    teams = db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=False).order_by(Team.id).all()
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
        round_teams[round_idx].append(idx)

    plans_idx = defaultdict(list)
    for (round_idx, round_entry) in enumerate(contents.data):
        for meeting in round_entry:
            host = None
            for team_idx in meeting:
                if team_idx in round_teams[round_idx]:
                    host = team_idx
                    break
            for team_idx in meeting:
                plans_idx[team_idx].append(host)

    def map_team(idx):
        return str(teams[idx].id)

    result = defaultdict(list)
    for team_idx in plans_idx:
        team_id = map_team(team_idx)
        for station in plans_idx[team_idx]:
            result[team_id].append(map_team(station))

    return result


def read_plan_file(args):
    result = {}
    if args.inform == "legacy":
        result = read_legacy_plan(args.in_file)
    elif args.inform == "dan_marc_partial":
        result = read_dan_marc_partial(args.in_file)
    return result


def cmd_convert_plan(args):
    result = read_plan_file(args)
    with open(args.out_file, "w+") as out_fn:
        json.dump(result, out_fn)


def cmd_print_plan(args):
    result = read_plan_file(args)
    teams = {}

    for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True).filter_by(backup=False):
        teams[str(team.id)] = team

    for entry in result:
        team = teams[entry]
        plan = result[entry]
        print "# %s ::" % team.name
        station_points = []
        last_station = None
        for station in plan:
            station_team = teams[station]
            dist = ""
            if last_station is not None:
                distance = db.session.query(RouteDistance).filter_by(location_from=last_station.location,
                                                                     location_to=station_team.location).first()
                dist = "[dist=%d]" % distance.distance
            print "+ %s %s" % (station_team.name, dist)
            station_points.append(MapPoint.from_team(station_team))
            last_station = station_team

        print "- route: %s" % openroute_link(station_points)
        print ""


def cmd_graph_plan(args):
    result = read_plan_file(args)
    process_plan(args.out_file, result)


def parse_args():
    args = ArgumentParser()

    subcommands = args.add_subparsers()
    args.add_argument("--inform", help="Specify the input format", required=True,
                      choices=("legacy", "dan_marc_partial"))
    args.add_argument("in_file", help="The file to convert")

    convert_parser = subcommands.add_parser("convert")
    convert_parser.add_argument("out_file", help="The output file")
    convert_parser.set_defaults(func=cmd_convert_plan)

    print_parser = subcommands.add_parser("print")
    print_parser.add_argument("--osm", action="store_true", help="build osm route links")
    print_parser.set_defaults(func=cmd_print_plan)

    graph_parser = subcommands.add_parser("graph", help="Build a clustering graph")
    graph_parser.add_argument("out_file", help="The filename for the output png")
    graph_parser.set_defaults(func=cmd_graph_plan)

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.func(args)