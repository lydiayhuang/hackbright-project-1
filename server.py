"""Airfare search: https://github.com/wordswithchung/hackbright-project"""

import calendar
from datetime import date, datetime, timedelta
from flask import (Flask, jsonify, render_template, redirect,
                   request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import Airfare, Airport, connect_to_db, db
from sqlalchemy import func


app = Flask(__name__)

app.secret_key = "randomKeyGenerated1837492RandomKeyGeneratedLadidadidah00!!"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    today = datetime.today()
    months = []
    # build a two-week buffer for displaying months available to book travel
    if today.day < calendar.monthrange(today.year, today.month)[1] / 2:
        months.append(today)
    # http://stackoverflow.com/a/12736311

    while len(months) < 12:
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        month = today + timedelta(days=days_in_month)
        months.append(month)
        today = month

    return render_template("homepage.html", months=months)

@app.route('/search', methods=['POST'])
def search():
    """User searches for flight."""

    depart = request.form.get("depart")[:3] # string
    month, year = request.form.get("month").split() # int representing month year
    duration = request.form.get("duration") # int representing # of days

    month = int(month)
    month_name = calendar.month_name[month]
    year = int(year)
    duration = int(duration)

    user_port = Airport.query.filter_by(code=depart).first()

    today = date.today()
    two_weeks = timedelta(days=14)
    safe_day = today + two_weeks

    c = calendar.monthcalendar(year, month)

    for i in range(4):
        if c[i][1]:
            if date(year, month, c[i][1]) > safe_day:
                global search_date
                search_date = date(year, month, c[i][1])

    end_date = search_date + timedelta(days=duration)
    end_date = end_date.strftime("%Y-%m-%d")
    start_date = search_date.strftime("%Y-%m-%d")

    ports = Airfare.locations(month_name, user_port) # determine ports to search

    kayak_urls = []
    for port in ports:
        kayak_urls.append("https://www.kayak.com/flights/" + port.depart + "-"
                          + port.arrive + "/" + start_date + "/" + end_date)

    return render_template("search.html", kayak_urls=kayak_urls,
                                          ports=ports)


@app.route('/autocomplete_port')
def autocomplete_airport_search():
    #https://designshack.net/articles/javascript/create-a-simple-autocomplete-with-html5-jquery/
    pass


if __name__ == "__main__":
    # Debug to true while building and testing app
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0', port=5000)
