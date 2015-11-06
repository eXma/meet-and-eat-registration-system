import unittest
import database as db
from mock import Mock
from planning.plan_build import build_meeting_entries, process_dan_marc_partial


class TestMeetingEntryBuild(unittest.TestCase):
    def test_unique_build(self):
        plan = {"1": ["1", "5", "8"],
                "2": ["2", "6", "9"],
                "3": ["3", "4", "7"],
                "4": ["1", "4", "9"],
                "5": ["2", "5", "7"],
                "6": ["3", "6", "8"],
                "7": ["1", "6", "7"],
                "8": ["2", "4", "8"],
                "9": ["3", "5", "9"]}

        entries = build_meeting_entries(plan)
        self.assertEqual(len(entries), 9 * 3)


def _mock_team(idx, distance):
    team = Mock(id=idx)
    team.location = Mock(center_distance=distance)
    return team


class TestDanMarcProcessing(unittest.TestCase):
    def setUp(self):
        db.init_session(drop=True)
        self.maxDiff = None

    # noinspection PySetFunctionToLiteral
    def test_processing(self):
        data_input = [[set([0, 22, 15]),
                       set([1, 26, 17]),
                       set([2, 18, 10]),
                       set([3, 20, 23]),
                       set([25, 19, 4]),
                       set([24, 11, 5]),
                       set([12, 13, 6]),
                       set([16, 9, 7]),
                       set([8, 21, 14])],
                      [set([9, 4, 6]),
                       set([24, 25, 10]),
                       set([19, 18, 11]),
                       set([23, 12, 7]),
                       set([3, 5, 13]),
                       set([2, 26, 14]),
                       set([8, 1, 15]),
                       set([16, 20, 22]),
                       set([0, 17, 21])],
                      [set([8, 17, 18]),
                       set([1, 10, 19]),
                       set([20, 14, 15]),
                       set([2, 11, 21]),
                       set([4, 13, 22]),
                       set([16, 5, 23]),
                       set([0, 24, 6]),
                       set([9, 12, 25]),
                       set([26, 3, 7])]]

        team_ids = [(3, 3.3973), (4, 4.3275), (5, 3.5067), (8, 3.8383),
                    (12, 3.3185), (13, 3.9332), (14, 4.3404), (16, 2.7504),
                    (19, 4.1135), (21, 3.3217), (23, 3.3088), (25, 4.4788),
                    (26, 3.8302), (28, 3.3362), (29, 4.4257), (30, 3.8994),
                    (31, 2.826), (33, 4.1537), (35, 3.3217), (38, 4.2229),
                    (39, 4.4579), (45, 3.6162), (46, 5.4541), (49, 3.2621),
                    (50, 3.9429), (51, 4.4788), (53, 2.9354)]

        expected = {'49': ['39', '30', '49'],
                    '53': ['14', '50', '53'],
                    '25': ['25', '45', '21'],
                    '26': ['33', '26', '35'],
                    '21': ['29', '13', '21'],
                    '23': ['46', '5', '23'],
                    '46': ['46', '3', '53'],
                    '45': ['46', '45', '35'],
                    '28': ['51', '13', '28'],
                    '29': ['29', '19', '23'],
                    '3': ['25', '3', '28'],
                    '5': ['38', '5', '49'],
                    '4': ['4', '19', '53'],
                    '8': ['4', '8', '23'],
                    '13': ['14', '13', '12'],
                    '12': ['33', '3', '12'],
                    '39': ['39', '8', '16'],
                    '38': ['38', '30', '16'],
                    '14': ['14', '8', '49'],
                    '16': ['25', '26', '16'],
                    '19': ['38', '19', '31'],
                    '31': ['29', '50', '31'],
                    '30': ['4', '30', '31'],
                    '51': ['51', '26', '12'],
                    '50': ['51', '50', '21'],
                    '35': ['39', '5', '35'],
                    '33': ['33', '45', '28']}

        # noinspection PyTypeChecker
        result = process_dan_marc_partial(data_input,
                                          [_mock_team(idx, dist)
                                           for (idx, dist) in team_ids])
        self.assertDictEqual(dict(result), expected)
