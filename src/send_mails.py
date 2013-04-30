#!python
from argparse import ArgumentParser
from teammails import informal_to_teams


def parse_args():
    args = ArgumentParser()

    args.add_argument("--nodebug", help="do really send the mails to the teams", action="store_true")

    subs = args.add_subparsers()
    informal = subs.add_parser("informal", help="send informal mails")
    informal.add_argument("-s", "--subject", help="set the mail subject", required=True)
    informal.add_argument("-t", "--templatename", help="set the name of the template to use", required=True)

    informal.set_defaults(func=cmd_send_informal)

    return args.parse_args()


def cmd_send_informal(args):
    informal_to_teams(args.templatename, args.subject, not args.nodebug)


if __name__ == "__main__":
    args = parse_args()
    args.func(args)