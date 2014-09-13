import os
import re
import urllib2
from flask import Flask, request, render_template, flash, redirect, url_for, session
from flask.ext.mail import Mail, Message
from mtpiufm import MtpIufmBrowser
app = Flask(__name__)

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
            return redirect(url_for('planning'))
        else:
            flash(u'Invalid username/password.', 'danger')
    return render_template('login.html')

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    session.pop('username')
    session.pop('password')
    return redirect(url_for('home'))

def is_email_address_valid(email):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", email):
        return False
    return True

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    errors = ''
    subject = ''
    message = ''
    sender = ''
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        sender = request.form.get('sender', app.config['DEFAULT_FROM_EMAIL'])
        if not subject or not message or not sender:
            errors = "All fields are required. "
        if not errors:
            # Validate the email address and raise an error if it is invalid
            if not is_email_address_valid(sender):
                errors = errors + "Please enter a valid email address."
        if not errors:
            msg = Message(
                subject=subject,
                body=message,
                sender=sender,
                recipients=app.config['ADMINS'])
            mail.send(msg)
            flash(u'Message sent.', 'success')
            return redirect(url_for('home'))
        else:
            flash(errors, 'danger')
    data = {
        'errors': errors,
        'subject': subject,
        'message': message,
        'sender': sender,
    }
    return render_template('contact.html', data=data)

@app.route('/error500/')
def error500():
    """
    Testing error 500.
    """
    # assert(False)
    raise Exception("Testing error 500.")
    return redirect(url_for('login'))


# config app
if os.environ.get('PRODUCTION'):
    app.config.from_object('settings.ProductionSettings')
else:
    app.config.from_object('settings.DevelopmentSettings')
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['DEFAULT_FROM_EMAIL'],
                               app.config['ADMINS'], app.config['EMAIL_SUBJECT_PREFIX'],
                               credentials = (
                                os.environ['SENDGRID_USERNAME'],
                                os.environ['SENDGRID_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
# useful for debugging in production
if os.environ.get('DEBUG'):
    app.debug = True
# config mail
mail = Mail(app)
if __name__ == '__main__':
    app.run(port=8000)
