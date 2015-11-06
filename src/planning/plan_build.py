import imp
import json
from collections import defaultdict

from sqlalchemy import not_

import database as db
from database.model import Team, MeetingEntry
from planning.rounds import round_data


def read_legacy_plan(in_file):
    with open(in_file, "r") as in_fn:
        data = json.load(in_fn)

    result = {}
    for entry in data:
        result[entry["team_id"][0]] = [station[0] for station in entry["plan"]]
    return result


def read_dan_marc_partial(in_file, group=None, separate=None, exclude=None):
    """Read Debug output prefixed with "data="

    :param exclude: List of teams to exclude from processing
    :param group: A group id to process
    :param separate: A list of teams to include
    :param in_file: The file with the result
    :return: The processed data
    """
    contents = imp.load_source("_dummy", in_file)
    return process_dan_marc_partial(contents.data,
                                    fetch_teams(group, separate, exclude))


def fetch_teams(group=None, separate=None, exclude=None):
    """Fetch a selection of teams

    :param exclude: List of teams to exclude from processing
    :type exclude: list[int] or None
    :param group: A group id to process
    :type group: int or None
    :param separate: A list of teams to include
    :type separate: list[int] or None
    :return: The selected teams as list
    :rtype: list[Team]
    """
    teams = db.session.query(Team).filter_by(deleted=False,
                                             confirmed=True,
                                             backup=False).order_by(Team.id)
    if separate is not None:
        teams = teams.filter(Team.id.in_(separate))
    if exclude is not None:
        teams = teams.filter(not_(Team.id.in_(exclude)))
    if group:
        teams = teams.filter_by(groups=group)

    return teams.all()


def process_dan_marc_partial(contents, team_data):
    """process Debug output prefixed with "data="

    :param team_data: A list of selected teams
    :type team_data: list[Team]
    :param contents: The parsed contents
    :return: The processed data
    """

    round_teams = {}
    team_list = []

    for (team, round_idx) in round_data(team_data):
        team_list.append(team)
        round_teams[team.id] = round_idx

    def iter_meeting(meeting_set):
        for idx in meeting_set:
            yield team_list[idx].id

    plans = defaultdict(list)
    for (round_idx, round_entry) in enumerate(contents):
        for meeting in round_entry:
            host = None
            participants = []
            for team_id in iter_meeting(meeting):
                participants.append(team_id)
                if round_teams[team_id] == round_idx:
                    host = team_id

            for team_id in participants:
                plans[team_id].append(host)

    return string_indexes(plans)


def string_indexes(team_data):
    result = defaultdict(list)

    for team in team_data:
        for station in team_data[team]:
            result[str(team)].append(str(station))

    return result


def read_database_plan():
    plans = defaultdict(list)
    for entry in db.session.query(MeetingEntry).order_by(MeetingEntry.plan_round):
        plans[entry.participant].append(entry.host)

    return string_indexes(plans)


def build_meeting_entries(plans):
    meeting_parts = set()
    for entry in plans:
        round_idx = 0
        for station in plans[entry]:
            part = MeetingEntry(host_team_id=int(station),
                                plan_round=round_idx,
                                participant_team_id=int(entry))
            meeting_parts.add(part)
            round_idx += 1

    return meeting_parts


def import_database(plans):
    db.session.add_all(build_meeting_entries(plans))
    db.session.commit()
