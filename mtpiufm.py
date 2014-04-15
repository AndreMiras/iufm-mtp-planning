#!/usr/bin/env python2

import os
import tempfile
import mechanize
import webbrowser

# https://ent.montpellier.iufm.fr/cas/index.jsp?service=http://ent.montpellier.iufm.fr/Login
# https://ent.montpellier.iufm.fr/cas/
# http://ent.montpellier.iufm.fr/Login
# https://ent.montpellier.iufm.fr/cas/?service=http://web2.montpellier.iufm.fr/WD110AWP/WD110Awp.exe/CONNECT/Planning
# http://web2.montpellier.iufm.fr/WD110AWP/WD110Awp.exe/CONNECT/Planning



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
        # to date -> default
        browser.form["A6"] 
        # format -> HTML
        HTML_OPTION = ["2"]
        browser.form["A4"] = HTML_OPTION
        resp = browser.submit()
        return resp.read()


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
