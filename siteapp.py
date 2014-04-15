import os
from flask import Flask, request, render_template, flash, redirect, url_for
import settings
from mtpiufm import MtpIufmBrowser
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY

@app.route('/')
def index():
    return redirect(url_for('login'))

def valid_login(username, password):
    mtpIufmBrowser = MtpIufmBrowser()
    return mtpIufmBrowser.login(username, password)

def show_planning(username, password):
    mtpIufmBrowser = MtpIufmBrowser()
    # TODO: do not login twice (the first is in valid_login
    mtpIufmBrowser.login(username, password)
    planning_html = mtpIufmBrowser.planning_html()
    # return render_template('planning.html', planning_html=planning_html)
    return planning_html

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            # return log_the_user_in(request.form['username'])
            return show_planning(request.form['username'],
                        request.form['password'])
        else:
            flash(u'Invalid username/password', 'danger')
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html')

@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.debug = settings.DEBUG
    app.run(port=8000)
