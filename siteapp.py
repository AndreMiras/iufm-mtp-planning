import urllib2
from flask import Flask, request, render_template, flash, redirect, url_for, session
import settings
from mtpiufm import MtpIufmBrowser
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

@app.template_filter('to_js_date')
def to_js_date(d):
    return d.strftime("Date('%Y/%m/%d %H:%M:%S')")

def redirect_url(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

@app.route('/')
def home():
    return render_template('home.html')

def valid_login(username, password):
    mtpIufmBrowser = MtpIufmBrowser()
    valid = mtpIufmBrowser.login(username, password)
    if valid:
        session['username'] = username
        session['password'] = password
    return valid

@app.route('/planning_html/')
def show_planning_html():
    """
    Used for failback and debugging purpose.
    """
    mtpIufmBrowser = MtpIufmBrowser()
    username = session.get("username", "")
    password = session.get("password", "")
    # TODO[perfs]: too bad to log twice
    if mtpIufmBrowser.login(username, password):
        try:
            return mtpIufmBrowser.planning_html()
        except urllib2.URLError as e:
            flash(u"Couldn't reach service (%s)." % e.reason, 'danger')
            return redirect(url_for('home'))
    return redirect(url_for('login', next=url_for("planning")))

@app.route('/planning/')
def planning():
    mtpIufmBrowser = MtpIufmBrowser()
    username = session.get("username", "")
    password = session.get("password", "")
    # TODO[perfs]: too bad to log twice
    if mtpIufmBrowser.login(username, password):
        try:
            # planning_html = mtpIufmBrowser.planning_html()
            timetable = mtpIufmBrowser.planning()
            return render_template('planning.html', timetable=timetable)
        except urllib2.URLError as e:
            flash(u"Couldn't reach service (%s)." % e.reason, 'danger')
            return redirect(url_for('home'))
    return redirect(url_for('login', next=url_for("planning")))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        valid = False
        try:
            valid = valid_login(request.form['username'],
                       request.form['password'])
        except urllib2.URLError as e:
            flash(u"Couldn't reach service (%s)." % e.reason, 'danger')
            return redirect(url_for('home'))
        if valid:
            return redirect(redirect_url())
        else:
            flash(u'Invalid username/password.', 'danger')
    return render_template('login.html')

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('username')
    session.pop('password')
    return redirect(url_for('home'))

@app.route('/hello/')
def hello():
    return 'Hello World!'

@app.route('/error500/')
def error500():
    """
    Testing error 500.
    """
    # assert(False)
    raise Exception("Testing error 500.")
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
