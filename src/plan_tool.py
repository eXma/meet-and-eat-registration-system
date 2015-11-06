#!env python

import json
import sys
from argparse import ArgumentParser

import database as db
from cfg.config import DB_CONNECTION
from database.model import Team, RouteDistance
from geotools import openroute_link, gmaps_link
from geotools.routing import MapPoint
from planning.cluster_graph import process_plan
from planning.plan_build import read_dan_marc_partial, read_legacy_plan, read_database_plan

db.init_session(connection_string=DB_CONNECTION)


def read_plan_file(args):
    result = {}
    if args.inform == "legacy":
        result = read_legacy_plan(args.file)
    elif args.inform == "dan_marc_partial":
        result = read_dan_marc_partial(args.file, args.group, args.separate, args.exclude)
    elif args.inform == "database":
        result = read_database_plan()
    return result


def cmd_convert_plan(args):
    result = read_plan_file(args)
    with open(args.result, "w+") as out_fn:
        json.dump(result, out_fn)


def cmd_print_plan(args):
    result = read_plan_file(args)
    teams = {}

    for team in db.session.query(Team).filter_by(deleted=False,
                                                 confirmed=True,
                                                 backup=False):
        teams[str(team.id)] = team

    for entry in result:
        team = teams[entry]
        plan = result[entry]
        print "# %s ::" % team.name.encode("utf8")
        station_points = []
        last_station = None
        for station in plan:
            station_team = teams[station]
            dist = ""
            if last_station is not None:
                distance = db.session.query(RouteDistance).filter_by(location_from=last_station.location,
                                                                     location_to=station_team.location).first()
                dist = "[dist=%d]" % distance.distance
            print "+ %s %s" % (station_team.name.encode("utf8"), dist)
            station_points.append(MapPoint.from_team(station_team))
            last_station = station_team

        if args.osm:
            print "- route (osm): %s" % openroute_link(station_points)
        if args.gmaps:
            print "- route (google): %s" % gmaps_link(station_points)
        print ""


def cmd_graph_plan(args):
    result = read_plan_file(args)
    process_plan(args.result, result, not args.annonymize, args.distance, args.labels)


def cmd_import_plan(args):
    if args.inform == "database":
        print "Cannot import from database as the database is the target!"
        sys.exit(255)

    result = read_plan_file(args)


def parse_args():
    args = ArgumentParser()

    subcommands = args.add_subparsers()
    args.add_argument("-f", "--inform", help="Specify the input format", required=True,
                      choices=("legacy", "dan_marc_partial", "database"))
    args.add_argument("-i", "--file", metavar="FILE", help="The file to convert")
    args.add_argument("-S", "--separate", type=int, metavar="I", nargs="+",
                      help="Separate the given ids to a new group",
                      required=False)
    args.add_argument("-E", "--exclude", type=int, metavar="I", nargs="+",
                      help="Exclude the given ids to a new group",
                      required=False)
    args.add_argument("-g", "--group", type=int, metavar="g", required=False,
                      help="Import data for a given group")

    convert_parser = subcommands.add_parser("convert")
    convert_parser.add_argument("-o", "--result", help="The output file")
    convert_parser.set_defaults(func=cmd_convert_plan)

    print_parser = subcommands.add_parser("print")
    print_parser.add_argument("--osm", action="store_true", help="build osm route links")
    print_parser.add_argument("--gmaps", action="store_true", help="build google maps route links")
    print_parser.set_defaults(func=cmd_print_plan)

    graph_parser = subcommands.add_parser("graph", help="Build a clustering graph")
    graph_parser.add_argument("-o", "--result", help="The filename for the output png")
    graph_parser.add_argument("-a", "--annonymize", help="Use numbers instead of names", action="store_true")
    graph_parser.add_argument("-d", "--distance", help="Use distances for graph lenghths", action="store_true")
    graph_parser.add_argument("-l", "--labels", help="Use distances for graph lenghths", action="store_true")
    graph_parser.set_defaults(func=cmd_graph_plan)

    import_parser = subcommands.add_parser("import")
    import_parser.set_defaults(func=cmd_import_plan)

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.func(args)
