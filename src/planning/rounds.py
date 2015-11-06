from collections import defaultdict
from math import floor


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


