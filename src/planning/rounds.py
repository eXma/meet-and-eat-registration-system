from math import floor
import database as db

from database.model import RoundAssignment


def distance_sort(a, b):
    if a.location.center_distance > b.location.center_distance:
        return -1
    if a.location.center_distance < b.location.center_distance:
        return 1
    return 0


def split_rounds(teams):
    max_working = len(teams) - (len(teams) % 3)
    divider = max_working / 3.0

    working = teams[:max_working]
    teams = sorted(working, distance_sort) + teams[max_working:]

    for idx, team in enumerate(teams):
        round_idx = 0
        if divider > 0:
            round_idx = min(int(floor(idx / divider)), 3)

        yield (team, round_idx)


def assign_default_rounds(teams):
    assignments = [RoundAssignment(team_id=team.id, round=round_idx)
                   for (team, round_idx) in split_rounds(teams)]

    db.session.query(RoundAssignment).delete()
    db.session.add_all(assignments)
    db.session.commit()


def round_data(teams):
    assignments = dict([(assign.team, assign.round) for assign in db.session.query(RoundAssignment)])
    unassigned = [team for team in teams if team not in assignments]

    for team in assignments:
        yield (team, assignments[team])

    for (team, round_idx) in split_rounds(unassigned):
        yield (team, round_idx)
