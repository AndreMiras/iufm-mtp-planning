import urllib2
from flask import Flask, request, render_template, flash, redirect, url_for
import settings
from mtpiufm import MtpIufmBrowser
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

@app.template_filter('to_js_date')
def to_js_date(d):
    return d.strftime("Date('%Y-%m-%d %H:%M:%S')")

@app.route('/')
def index():
    return redirect(url_for('login'))

def valid_login(username, password):
    mtpIufmBrowser = MtpIufmBrowser()
    return mtpIufmBrowser.login(username, password)

def show_planning(username, password):
    mtpIufmBrowser = MtpIufmBrowser()
    # TODO: do not login twice (the first is in valid_login)
    mtpIufmBrowser.login(username, password)
    # planning_html = mtpIufmBrowser.planning_html()
    timetable = mtpIufmBrowser.planning()
    return render_template('planning.html', timetable=timetable)

@app.route('/planning_html/', methods=['GET', 'POST'])
def show_planning_html():
    """
    Used for failback and debugging purpose.
    """
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        mtpIufmBrowser = MtpIufmBrowser()
        mtpIufmBrowser.login(username, password)
        planning_html = mtpIufmBrowser.planning_html()
        return planning_html
    return render_template('login.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            if valid_login(request.form['username'],
                           request.form['password']):
                # return log_the_user_in(request.form['username'])
                return show_planning(request.form['username'],
                            request.form['password'])
            else:
                flash(u'Invalid username/password.', 'danger')
        except urllib2.URLError as e:
            flash(u"Couldn't reach service (%s)." % e.reason, 'danger')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html')

@app.route('/hello')
def hello():
    return 'Hello World!'

@app.route('/error500')
def error500():
    """
    Testing error 500.
    """
    assert(False)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.debug = settings.DEBUG
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler(settings.EMAIL_HOST,
                                   settings.DEFAULT_FROM_EMAIL,
                                   settings.ADMINS, EMAIL_SUBJECT_PREFIX)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    app.run(port=8000)
