#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import sqlite3
import json, string, random
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for, make_response, escape, g, abort

app = Flask(__name__)
app.config.from_object(__name__) ## TODO: Not sure where this pulls from

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'alfred.db'),
    USERNAME='admin', ## Note these aren't currently used
    PASSWORD='default' ## Note these aren't currently used
)) ## VARS must be UPPERCASE
app.config.from_envvar('FLASKR_SETTINGS', silent=True) # To use, initialize env var to config file
### TODO: Implement instance folders; http://flask.pocoo.org/docs/0.11/config/#instance-folders

### TODO: Refactor into modules: http://flask.pocoo.org/docs/0.11/patterns/packages/#larger-applications
def rand_ascii(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def connect_db():
    """ Connects to the specific database
    """
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

@app.cli.command('dropdb')
def dropdb_command():
    """Drop the database."""
    try:
        os.remove( app.config['DATABASE'] )
        print 'Deleted the database.'
    except:
        print 'Error deleting', app.config['DATABASE']
        pass

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
