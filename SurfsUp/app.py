# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import os
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################


os.chdir(os.path.dirname(os.path.realpath(__file__)))

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
Base = automap_base()
                       
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Display landing page routes
@app.route("/")
def welcome():
    html = (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )
    return html

#Define precipitation route, reflecting queries from precipitation analysis
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_day = session.query(func.max(measurement.date)).first()[0]
    last_year = dt.date.fromisoformat(last_day) - dt.timedelta(days=365)

    precipitation_api = session.query(measurement.date, func.avg(measurement.prcp))\
        .filter(measurement.date >= last_year)\
        .group_by(measurement.date)\
        .all()

#Covert to a dictionary and return the JSON representation
    prcp_dict = {}
    for row in precipitation_api:
        prcp_dict[row[0]] = row[1]
    return jsonify(prcp_dict)


#Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    #query all stations data
    results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    #convert row objects to tuples so that they can be serialized
    results = [tuple(row) for row in results]
    return jsonify(results)

#Define the tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    #query most active station date and temp date for the last year
    station_temp = session.query(measurement.tobs).filter(measurement.date <= '2017-08-18', measurement.date >= '2016-08-18')\
        .filter(measurement.station == 'USC00519281').all()
    #convert row objects to tuples so that they can be serialized
    station_temp = [tuple(row) for row in station_temp]
    return jsonify(station_temp)

#Define a start route
@app.route("/api/v1.0/<start>")
def get_temperature_start(start):
    session = Session(engine)

    #Query for specified start date, query the min, average and max temparature

    tmin = session.query(func.min(measurement.tobs)).filter(measurement.date >= start).first()
    tmax = session.query(func.max(measurement.tobs)).filter(measurement.date >= start).first()
    tavg = session.query(func.avg(measurement.tobs)).filter(measurement.date >= start).first() 

    

    results = [tmin[0], tmax[0], tavg[0]]

    return jsonify(results)

# #Define a start and end route
@app.route('/api/v1.0/<start>/<end>')
def get_temperature_start_end(start, end):
    session = Session(engine)

    #Query for specified start and end date, query the min, average and max temparature
    tmin = session.query(func.min(measurement.tobs)).filter(start <= measurement.date <= end).first()
    tmax = session.query(func.max(measurement.tobs)).filter(start <=measurement.date <= end).first()
    tavg = session.query(func.avg(measurement.tobs)).filter(start <= measurement.date <= end).first() 

    results = [tmin[0], tmax[0], tavg[0]]

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)