# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Create connection to database
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread':False})

# Reflect database to local object
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create references to database tables.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session for querying database
session = Session(engine)


# Create instance of Flask application
app = Flask(__name__)

# Build Routes for and functions for climate anlysis.
# -----------------------------------------------------------

# Root route - Provides list of available routes stemming from the root.

@app.route('/')
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!<br>
    Available Routes:<br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br>
    <a href="/api/v1.0/stations">/api/v1.0/stations</a><br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br>
    <a href="/api/v1.0/temp/start/end">/api/v1.0/temp/start/end</a><br>
    ''')


@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)