import unittest

from planning.plan_build import build_meeting_entries


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
