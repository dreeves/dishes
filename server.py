#!/usr/bin/env python
# -*- coding: utf-8 -*-

#       _                              
#      | |                             
#    __| |_ __ ___  __ _ _ __ ___  ___ 
#   / _` | '__/ _ \/ _` | '_ ` _ \/ __|
#  | (_| | | |  __/ (_| | | | | | \__ \
#   \__,_|_|  \___|\__,_|_| |_| |_|___/ .
#
# A 'Fog Creek'–inspired demo by Kenneth Reitz™

import os
import math
from flask import Flask, request, render_template, jsonify
import random
import pytz
from datetime import datetime, timedelta

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, 
            static_folder='public', 
            static_url_path='/public', # o3 said to add this
            template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret = os.environ.get('SECRET')

who_can_do_dishes = ["Cantor", "Faire", "Daddy"]

class History():
  def __init__(self, *args):
    self.name = args[0]
    self.count = args[1]
    self.percent = args[2]
    
  name = ''
  count = 0
  percent = 0

def to_pacific(in_date):
  utc = pytz.timezone("utc")
  utc_date = utc.localize(in_date)
  tz = pytz.timezone('US/Pacific')
  return utc_date.astimezone(tz)

def select_for_date(the_day):
  seed = int(the_day.strftime('%Y%m%d'))
  random.seed(seed)
  return random.choice(who_can_do_dishes)


@app.after_request
def apply_kr_hello(response):
    """Adds some headers to all responses."""
  
    # Made by
    if 'MADE_BY' in os.environ:
        response.headers["X-Was-Here"] = os.environ.get('MADE_BY')
    
    # Powered by 
    response.headers["X-Powered-By"] = os.environ.get('POWERED_BY')
    return response


@app.route('/')
def homepage():
    """Displays the homepage."""
    today = to_pacific(datetime.now())
    seed = int(today.strftime('%Y%m%d'))
    random.seed(seed)
    name = random.choice(who_can_do_dishes)
    return render_template('index.html', name=name, today=today.date())
  
@app.route('/history')
@app.route('/history/<int:num_days_history>')
def history(num_days_history=365):
  
  start_date = to_pacific(datetime.now() - timedelta(days=num_days_history-1))
  dishes_history = {p:History(p, 0, 0)for p in who_can_do_dishes}
  
  current_date = start_date
  while current_date < to_pacific(datetime.now()):
    dishes_history[select_for_date(current_date)].count += 1
    current_date += timedelta(days=1)
  
  for p in dishes_history.values():
    p.percent = int(p.count / float(num_days_history) * 100)
  
  return render_template("history.html", start_date=start_date.date(), history=dishes_history, total=num_days_history)
    

if __name__ == '__main__':
    app.run()
