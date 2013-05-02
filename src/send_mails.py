#!env python

from argparse import ArgumentParser
from plan_tool import read_plan_file
from teammails import informal_to_teams, plans_to_teams


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
    plan.add_argument("in_file", help="The input file with the plan")
    plan.set_defaults(func=cmd_send_planmails)

    return args.parse_args()


def cmd_send_informal(args):
    informal_to_teams(args.templatename, args.subject, not args.nodebug)


def cmd_send_planmails(args):
    results = read_plan_file(args)
    plans_to_teams(results, not args.nodebug)


if __name__ == "__main__":
    args = parse_args()
    args.func(args)
