#!/usr/bin/env python2

import os
import re
import tempfile
import mechanize
import webbrowser
from datetime import datetime, timedelta
from BeautifulSoup import BeautifulSoup

# https://ent.montpellier.iufm.fr/cas/index.jsp?service=http://ent.montpellier.iufm.fr/Login
# https://ent.montpellier.iufm.fr/cas/
# http://ent.montpellier.iufm.fr/Login
# https://ent.montpellier.iufm.fr/cas/?service=http://web2.montpellier.iufm.fr/WD110AWP/WD110Awp.exe/CONNECT/Planning
# http://web2.montpellier.iufm.fr/WD110AWP/WD110Awp.exe/CONNECT/Planning

class Course:

    def __init__(self, datetime_from):
        self.course_name = ""
        self.datetime_from = datetime_from
        self.datetime_to = datetime_from + timedelta(hours=+1)
        self.course_location = ""
        self.course_room = ""
        self.teacher = ""

    def __str__(self):
        d = {
            "course_name": self.course_name,
            "datetime_from": self.datetime_from,
            "datetime_to": self.datetime_to,
            "teacher": self.teacher,
        }
        return str(d)

class TimeTable:

    def __init__(self):
        self.courses = []

    def __str__(self):
        return " ".join(str(course) for course in self.courses)

    def add_course(self, course):
        self.courses.append(course)

    def courses(self):
        """
        Returns the list of ordered (by datetime) courses.
        """
        return sorted(self.courses, key=lambda x: x.datetime_from, reverse=True)

class MtpIufmBrowser:

    def __init__(self):
        self.LOGIN_URL = "https://ent.montpellier.iufm.fr/cas/"
        self.PLANNING_URL = "http://web2.montpellier.iufm.fr/WD110AWP/WD110Awp.exe/CONNECT/Planning"
        self.browser = mechanize.Browser()
        # ignores HTTP Error 403: request disallowed by robots.txt
        self.browser.set_handle_robots(False)

    def login(self, username, password):
        """
        Returns True on login success.
        """
        self.username = username
        self.password = password
        browser = self.browser
        browser.open(self.LOGIN_URL)
        browser.select_form(name="login_form")
        browser.form['username'] = username
        browser.form['password'] = password
        resp = browser.submit()
        return "mot de passe invalide" not in resp.read()

    def planning_html(self):
        """
        Returns planning HTML code.
        """
        browser = self.browser
        # browses to planning form
        # TODO: verify we don't do things twice
        browser.open(self.PLANNING_URL)
        browser.follow_link(url_regex='/CONNECT/Planning')
        # posts planning form
        browser.select_form(name="MENU")
        # from date -> default
        browser.form["A1"] 
        # to date -> 4 weeks ahead
        browser.form["A6"] = ['4']
        # format -> HTML
        HTML_OPTION = ["2"]
        browser.form["A4"] = HTML_OPTION
        resp = browser.submit()
        return resp.read()

    def planning(self):
        timetable = TimeTable()
        courses_parsed = self.planning_parsed()
        for course_parsed in courses_parsed:
            course = Course(course_parsed["datetime_from"])
            course.datetime_to = course_parsed["datetime_to"]
            course.course_name = course_parsed["eu_course"]
            course.course_location = course_parsed["location"]
            course.course_room = course_parsed["room"]
            course.teacher = course_parsed["teacher"]
            timetable.add_course(course)
        return timetable


    def planning_parsed(self):
        html = self.planning_html()
        courses_dirty = self._planning_parsed_level1(html)
        courses_clean = self._planning_parsed_level2(courses_dirty)
        return courses_clean

    def _planning_parsed_level1(self, html):
        """
        Planning parsed with Beautiful Soup.
        The HTML planning is presented as such:
        day, date, time         | group, teacher    | location
        education-unit, course  |
        The HTML is parsed and returned as a course dictionary.
        """
        # This would actually be a pain in the ass to parse because the
        # way the have done it. No unique id, nested tables all over the place...
        # Thanks PCSoft.
        soup = BeautifulSoup(html)
        universities = soup.findAll('a', {'class':'institution'})
        td_elems = soup.findAll('td', {'class':'l-5'})
        td_texts = [BeautifulSoup(td.text, convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0] for td in td_elems]
        date_regex = r".* ((\d{1,2})/(\d{1,2})/(\d{2,4})).*(\d{1,2} h \d{1,2}) \S (\d{1,2} h \d{1,2})"
        courses = []
        i = 0
        while i < len(td_texts) - 5:
            day_date_time = td_texts[i]
            group_teacher = td_texts[i + 1]
            eu_course = td_texts[i + 2]
            location = td_texts[i + 3]
            room = td_texts[i + 4]
            # sometimes the room isn't provided so that i + 4 will be the next date element
            match = re.search(date_regex, room)
            if match:
                room = None
                i -= 1
            course_dict = {
                "day_date_time": day_date_time,
                "group_teacher": group_teacher,
                "eu_course": eu_course,
                "location": location,
                "room": room,
            }
            # sometimes another element is added just before the next datetime element
            # so let's verify the text is the expected one (DD/MM/YYYY HH h MM \S HH h MM)
            match = re.search(date_regex, td_texts[i + 5])
            if not match:
                course_dict.update({"extra_info": td_texts[i + 5]})
                i += 1
            courses.append(course_dict)
            i += 5
        return courses

    def _planning_parsed_level2(self, courses_dirty):
        """
        Parses courses:
          - split day_date_time
          - extract teacher name
        """
        courses = courses_dirty
        for course in courses_dirty:
            # parsing date and time
            day_date_time = course.pop("day_date_time")
            match = re.search(r".* ((\d{1,2})/(\d{1,2})/(\d{2,4}))", day_date_time)
            date_str = match.group(1)
            date = datetime.strptime(date_str, "%d/%m/%Y").date()
            time_from_str = re.search(r".* (\d{1,2} h \d{1,2}) \S (\d{1,2} h \d{1,2})", day_date_time).group(1)
            time_from_str = time_from_str.replace(" h ", "h")
            time_to_str = re.search(r".* (\d{1,2} h \d{1,2}) \S (\d{1,2} h \d{1,2})", day_date_time).group(2)
            time_to_str = time_to_str.replace(" h ", "h")
            datetime_from_str = date_str + " " + time_from_str
            datetime_to_str = date_str + " " + time_to_str
            datetime_from = datetime.strptime(datetime_from_str, "%d/%m/%Y %Hh%M")
            datetime_to = datetime.strptime(datetime_to_str, "%d/%m/%Y %Hh%M")
            # extracts teacher name from group + teacher
            group_teacher = course.pop("group_teacher")
            # teacher can be empty
            teacher = re.search(r".* \((.*)\)", group_teacher).group(1)
            course.update({
                "datetime_from": datetime_from,
                "datetime_to": datetime_to,
                "teacher": teacher,
            })
        return courses


def main():
    from cred import credential
    mtpIufmBrowser = MtpIufmBrowser()
    mtpIufmBrowser.login(
        credential["username"],
        credential["password"])
    html = mtpIufmBrowser.planning_html()
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(html)
    f.close()
    new = 2 # open in a new tab, if possible
    webbrowser.open(f.name, new=new)
    # os.unlink(f.name)

if __name__ == "__main__":
    main()
