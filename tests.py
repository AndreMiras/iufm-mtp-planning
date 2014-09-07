import unittest
import datetime
from mtpiufm import MtpIufmBrowser

class TestMtpIufmBrowser(unittest.TestCase):

    def setUp(self):
        self.mtpIufmBrowser = MtpIufmBrowser()

    def test_planning_parsed_level1_and_2(self):
        f = open("docs/planning_fixture.html")
        html = f.read()
        f.close()
        # level1
        courses_dirty = self.mtpIufmBrowser._planning_parsed_level1(html)
        self.assertEqual(len(courses_dirty), 6)
        course0 = courses_dirty[0]
        self.assertTrue("16/04/2014" in course0['day_date_time'])
        self.assertTrue("10 h 00" in course0['day_date_time'])
        self.assertTrue("12 h 30" in course0['day_date_time'])
        self.assertTrue("Firstname" in course0['group_teacher'])
        self.assertTrue("Lastname" in course0['group_teacher'])
        self.assertTrue("Culture pro" in course0['eu_course'])
        # level2
        courses_clean = self.mtpIufmBrowser._planning_parsed_level2(courses_dirty)
        self.assertEqual(len(courses_dirty), 6)
        course0 = courses_clean[0]
        self.assertEqual(course0['datetime_from'], datetime.datetime(2014, 4, 16, 10, 0))
        self.assertEqual(course0['datetime_to'], datetime.datetime(2014, 4, 16, 12, 30))
        self.assertTrue("Culture pro" in course0['eu_course'])
        self.assertEqual(course0['location'], "FDE site de Montpellier")
        self.assertEqual(course0['room'], "J1")
        self.assertTrue("Firstname" in course0['teacher'])
        self.assertTrue("Lastname" in course0['teacher'])
        # level1&2 with different fixture
        # this fixture has some extra_info column (e.g. evaluation) and an empty teacher
        f = open("docs/planning_fixture2.html")
        html = f.read()
        f.close()
        courses_dirty = self.mtpIufmBrowser._planning_parsed_level1(html)
        courses_clean = self.mtpIufmBrowser._planning_parsed_level2(courses_dirty)
        self.assertEqual(len(courses_dirty), 16)
        course0 = courses_clean[0]
        # level1&2 with different fixture
        # this fixture has an empty room element
        f = open("docs/planning_fixture3.html")
        html = f.read()
        f.close()
        courses_dirty = self.mtpIufmBrowser._planning_parsed_level1(html)
        courses_clean = self.mtpIufmBrowser._planning_parsed_level2(courses_dirty)
        self.assertEqual(len(courses_dirty), 12)
        course0 = courses_clean[0]

if __name__ == '__main__':
    unittest.main()
