#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import datetime
## TODO: Use Jinja Filter for template formatting: http://jinja.pocoo.org/docs/dev/api/#custom-filters
import sqlite3
from bs4 import BeautifulSoup
from netscape_bookmarks import parse_netscape_bookmarks
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

@app.route('/bookmarklet')
def srv_bookmarklet():
    """ Serve bookmarklet
    """

    return render_template('bookmarklet.js')

### TODO: Refactor into modules: http://flask.pocoo.org/docs/0.11/patterns/packages/#larger-applications
def rand_ascii(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

### TODO: NOT USED YET - maybe ever
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

@app.route('/entries', methods=['GET', 'POST', 'PUT', 'DELETE'])
def entries():

    if request.method == 'GET':
        cur = query_db('select * from links order by id desc')
        entries = [ dict(c) for c in cur ]
        for e in entries:
            e['tags'] = [t for t in re.split(r"[, ]", e['tags']) if t is not '']
        return render_template('show_entries.html', entries=entries)

    elif request.method == 'POST' or request.method == 'PUT': # Not strictly correct
        db.execute('insert into links (title, url, time, tags, comment) values (?, ?, ?, ?, ?)',
                    [ request.form['title'], request.form['url'], datetime.date.today(),
                      request.form['tags'], request.form['comment'] ])
        db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('/'))
    elif request.method == 'DELETE':
        abort(501)
    else: ## Something bad happend
        app.logger.error("Entries: HOW DID WE GET HERE?")
        abort(500)

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
    ## Added the second os.() check to prevent creating null file
    if hasattr(g, 'sqlite_db') and os.path.isfile( app.config['DATABASE'] ):
        g.sqlite_db.close()

@app.cli.command('import')
#@app.cli.argument('-n', prompt='filename', help='The filename of the exported delicious.html')
def importdb_command():
    """ Imports delicious export into the database.
    """
    db = get_db()
    import_filename = 'delicious(2)-Aug.28.html'

    #with BeautifulSoup( open(import_filename, "r").read(), "html.parser") as old_links:
    #    pass

    #soup = BeautifulSoup( open(import_filename, "r"), "html.parser" )
    with open(import_filename, "r") as f:
        bookmarks = parse_netscape_bookmarks( f.read() )

    app.logger.debug("Found %d bookmarks" % len(bookmarks))
    for link in bookmarks:

        tags = " ".join( [t for t in re.split(r"[, ]", link['tags']) if t is not ''] )

        if link.get('note', None):
            link['note'] = link['note'].decode('utf-8')
        else:
            link['note'] = None

        data = { 'line': link['line'] }

        db.execute('insert into links (title, private, url, time, tags, comment, json_blob) values (?, ?, ?, ?, ?, ?, ?)', [ link['title'], link['private'], link['url'], link['posix_timestamp'], tags, link['note'], json.dumps( data ) ])

    db.commit()
    app.logger.debug('Imported links into the database.')

@app.cli.command('initdb')
def initdb_command():
    """ Initializes the database.
    """
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

    app.logger.debug('Initialized the database.')

@app.cli.command('dropdb')
def dropdb_command():
    """ Drop the database.
    """
    try:
        os.remove( app.config['DATABASE'] )
        app.logger.debug('Deleted the database.')
    except:
        app.logger.error('Error deleting %s' % (app.config['DATABASE']) )
        pass

@app.route('/logout', methods=['POST'])
def logout():
    """ Logout User - by clearing cookie
        Note: Maybe a session var should be used but woud prefer greater persistence
    """
    error = None

    flash('You were successfully logged out', 'info')
    resp = redirect(url_for('index'))
    resp.set_cookie('username', '', expires=0)
    return resp

@app.route('/login', methods=['POST'])
def login():
    """ Login the user - currently no auth execute
    """
    ## TODO: Eventually make this test something app.config maybe but OAuth better
    error = None

    if request.method == 'POST':
        ## Presently not validating auth
        user = request.form['username']
        pw = request.form['password']
        app.logger.debug('%s (%s) logged in' % (user, pw) )

        resp = redirect(url_for('index'))
        if (user == app.config['USERNAME']) and (pw == app.config['PASSWORD']):
            flash('You were successfully logged in', 'info')
            # Or: session['username'] = request.form['username']
            resp.set_cookie('username', escape( request.form['username']) )
        else:
            flash('You were not successfully logged in', 'danger')

        return resp

    ## SHOULD Never Happen, but maybe with a GET
    return render_template('index.html', error="Invalid username/password")

@app.route("/")
def index():
    """ Load Index Page
    """
    data = { }

    data['username'] = request.cookies.get('username')
    app.logger.debug('%s accessing /' % (data['username']) )

    if data['username']:
        cur = query_db('select * from links order by id desc limit 5')
        entries = [ dict(c) for c in cur ]
        for e in entries:
            e['tags'] = [t for t in re.split(r"[, ]", e['tags']) if t is not '']
        data['links'] = entries
    else:
        entries = None

    data['links'] = entries
    return render_template('index.html', data=data)

if __name__ == "__main__":

    config = { }

    ## TODO: Replace this with flask config loading
    try:
        with open('secret.json', 'r') as config_file:
            config = json.load(config_file)

        app.logger.debug("Config Loaded: %s" % config)
        app.secret_key = config['app_secret_key']
    except:
        app.secret_key = rand_ascii()
        app.logger.debug("Auto Generated Secret: %s" % (app.secret_key))

        config['app_secret_key'] = app.secret_key
        with open('secret.json', 'w') as config_file:
            json.dump(config, config_file)

    app.run()
