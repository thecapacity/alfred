#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json, string, random
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for, make_response, escape

app = Flask(__name__)

def rand_ascii(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route("/")
def index():
    return render_template ('index.html')

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
