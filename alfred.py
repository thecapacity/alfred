#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json, string, random
from flask import Flask, flash, jsonify, render_template, request, session, redirect, url_for, make_response, escape

app = Flask(__name__)

@app.route("/")
def index():
    return render_template ('index.html')

if __name__ == "__main__":
    app.run()
