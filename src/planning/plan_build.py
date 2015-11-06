import imp
import json
from collections import defaultdict
from math import floor
import database as db
from database.model import Team, MeetingEntry
from sqlalchemy import not_


def read_legacy_plan(in_file):
    with open(in_file, "r") as in_fn:
        data = json.load(in_fn)

    result = {}
    for entry in data:
        result[entry["team_id"][0]] = [station[0] for station in entry["plan"]]
    return result


def read_dan_marc_partial(in_file, group=None, seperate=None, exclude=None):
    """Debug output prefixed with "data="

    :param in_file: The file with the result
    :return: The processed data
    """
    contents = imp.load_source("_dummy", in_file)

    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id)
    if seperate is not None:
        teams = teams.filter(Team.id.in_(seperate))
    if exclude is not None:
        teams = teams.filter(not_(Team.id.in_(exclude)))
    if group:
        teams = teams.filter_by(groups=group)

    teams = teams.all()
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


def read_database_plan():
    plans = defaultdict(list)
    for entry in db.session.query(MeetingEntry).order_by(MeetingEntry.plan_round):
        plans[str(entry.participant)].append(str(entry.host))

    return plans
