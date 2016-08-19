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

def query_db(query, args=(), one=False):
    """ Sample Usage:

    for user in query_db('select * from users'):
        print user['username'], 'has the id', user['user_id']

    # Or if you just want a single result:
    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print 'No such user'
    else:
        print the_username, 'has the id', user['user_id']
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/entries', methods=['GET', 'POST'])
def entries():
    db = get_db()

    if request.method == 'GET':
        cur = query_db('select * from links order by id desc')
        entries = [ dict(c) for c in cur ]
        return render_template('show_entries.html', entries=entries)

    if request.method == 'POST':
        db.execute('insert into links (title, url, time, tags, comment) values (?, ?, ?, ?, ?)',
                    [ request.form['title'], request.form['url'], datetime.date.today(),
                      request.form['tags'], request.form['comment'] ])
        db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('/'))

def connect_db():
    """ Connects to the specific database
    """
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """ Opens a new database connection if there is none yet
        for the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """ Closes the database again at the end of the request
    """
    if hasattr(g, 'sqlite_db') and os.path.isfile( app.config['DATABASE'] ):
        g.sqlite_db.close()

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
