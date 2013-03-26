from math import sqrt
from random import random
import database as db
from database.model import Team, Members, Location


def make_dummy_data(num_teams, confirmed=True):
    for idx in range(num_teams):
        team = Team(name="Team %d" % idx,
                    confirmed=confirmed)
        db.session.add(team)

        for member_idx in range(3):
            member = Members(name="Member%d from team%d" % (member_idx, idx),
                             team = team)
            db.session.add(member)

        lat_rand = (0.5 - random()) * 0.1
        lon_rand = (0.5 - random()) * 0.1
        pseudo_dist = sqrt(lat_rand ** 2 + lon_rand **2)
        lat = 51.0322627 + lat_rand
        lon = 13.7071665 + lon_rand

        location = Location(street="Teststreet %d" % idx,
                            zip_no="01217",
                            extra="",
                            lat=lat,
                            lon=lon,
                            center_distance=pseudo_dist,
                            team=team)
        db.session.add(location)
    db.session.commit()
