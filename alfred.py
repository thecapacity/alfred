#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import json, string, random
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for, make_response, escape

app = Flask(__name__)
app.config.from_object(__name__) ## TODO: Not sure where this pulls from

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'alfred.db'),
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def rand_ascii(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/logout', methods=['POST'])
def logout():
    error = None

    flash('You were successfully logged out', 'info')
    resp = redirect(url_for('index'))
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route('/login', methods=['POST'])
def login():
    error = None

    if request.method == 'POST':
        ## Presently not validating auth
        print request.form['username'], request.form['password']

        flash('You were successfully logged in', 'info')
        resp = redirect(url_for('index'))
        resp.set_cookie('username', escape( request.form['username']) )
        # Or: session['username'] = request.form['username']

        return resp

    return render_template('index.html', error="Invalid username/password")

@app.route("/")
def index():
    data = { }

    data['username'] = request.cookies.get('username')
    print "Username:", data['username']

    #resp = make_response( render_template('index.html', data=data) )
    #resp.set_cookie('username', '', expires=0)
    #return resp

    return render_template('index.html', data=data)

if __name__ == "__main__":

    config = { }

    try:
        with open('secret.json', 'r') as config_file:
            config = json.load(config_file)

        print "Config Loaded:", config
        app.secret_key = config['app_secret_key']
    except:
        app.secret_key = rand_ascii()
        print "Auto Generated Secret:", app.secret_key

        config['app_secret_key'] = app.secret_key
        with open('secret.json', 'w') as config_file:
            json.dump(config, config_file)

    app.run()
