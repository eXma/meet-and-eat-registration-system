#!env python

from argparse import ArgumentParser
import json

import database as db
from database.model import Team, RouteDistance
from geotools import openroute_link
from geotools.routing import MapPoint
from webapp.cfg.config import DB_CONNECTION


db.init_session(connection_string=DB_CONNECTION)


def read_legacy_plan(in_file):
    with open(in_file, "r") as in_fn:
        data = json.load(in_fn)

    result = {}
    for entry in data:
        result[entry["team_id"][0]] = [station[0] for station in entry["plan"]]
    return result


def read_plan_file(args):
    result = {}
    if args.inform == "legacy":
        result = read_legacy_plan(args.in_file)
    elif args.inform == "dan_marc":
        print "to be implemented"
    return result


def cmd_convert_plan(args):
    result = read_plan_file(args)
    with open(args.out_file, "w+") as out_fn:
        json.dump(result, out_fn)


def cmd_print_plan(args):
    result = read_plan_file(args)
    teams = {}

    for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True):
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


def parse_args():
    args = ArgumentParser()

    subcommands = args.add_subparsers()
    args.add_argument("--inform", help="Specify the input format", required=True,
                      choices=("legacy", "dan_marc"))
    args.add_argument("in_file", help="The file to convert")

    convert_parser = subcommands.add_parser("convert")
    convert_parser.add_argument("out_file", help="The output file")
    convert_parser.set_defaults(func=cmd_convert_plan)

    print_parser = subcommands.add_parser("print")
    print_parser.add_argument("--osm", action="store_true", help="build osm route links")
    print_parser.set_defaults(func=cmd_print_plan)

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.func(args)