#!env python

from argparse import ArgumentParser
from plan_tool import read_plan_file
from promo import send_spam
from teammails import informal_to_teams, plans_to_teams, emergency_plan_routes


def parse_args():
    args = ArgumentParser()

    args.add_argument("--nodebug", help="do really send the mails to the teams", action="store_true")

    subs = args.add_subparsers()
    informal = subs.add_parser("informal", help="send informal mails")
    informal.add_argument("-s", "--subject", help="set the mail subject", required=True)
    informal.add_argument("-t", "--templatename", help="set the name of the template to use", required=True)
    informal.set_defaults(func=cmd_send_informal)

    plan = subs.add_parser("plan", help="send the plan mails")
    plan.add_argument("--inform", required=True, choices=("legacy", "dan_marc_partial"),
                      help="select the input format for the plan")
    plan.add_argument("--file", help="The input file with the plan")
    plan.add_argument("-S", "--separate", type=int, metavar="I", nargs="+",
                      help="Separate the given ids to a new group",
                      required=False)
    plan.add_argument("-E", "--exclude", type=int, metavar="I", nargs="+",
                      help="Exclude the given ids to a new group",
                      required=False)
    plan.add_argument("-g", "--group", type=int, metavar="G", required=False,
                      help="Select a group to sent the mails")
    plan.set_defaults(func=cmd_send_planmails)

    emergency_routes = subs.add_parser("emergency_routes", help="send the fixed route links")
    emergency_routes.add_argument("--inform", required=True, choices=("legacy", "dan_marc_partial"),
                                  help="select the input format for the plan")
    emergency_routes.add_argument("--file", help="The input file with the plan")
    emergency_routes.set_defaults(func=cmd_send_emergency_routes)

    spam = subs.add_parser("spam", help="Send event information to a list of former teams")
    spam.add_argument("-a", "--addresses", required=True,
                      help="A file with a list of space, comma or semicolon separated recipients")
    spam.set_defaults(func=cmd_send_spam)


    return args.parse_args()


def cmd_send_informal(args):
    informal_to_teams(args.templatename, args.subject, not args.nodebug)


def cmd_send_planmails(args):
    results = read_plan_file(args)
    plans_to_teams(results, not args.nodebug, args.group, args.separate, args.exclude)


def cmd_send_emergency_routes(args):
    results = read_plan_file(args)
    emergency_plan_routes(results, not args.nodebug)


def cmd_send_spam(args):
    send_spam(args.addresses, not args.nodebug)


if __name__ == "__main__":
    args = parse_args()
    args.func(args)
