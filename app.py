import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

## Setup Database

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


## Setup Flask
app = Flask(__name__)

## Set Flask Routes
@app.route("/")
def welcome():
    return (f"Welcome to the Precipitation and Temperature Records of Hawaii!<br/>"
        f"This page list all available api routes.<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature of previous year: /api/v1.0/tobs<br/>"
        f"Min, Ave, and Max temperature from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Min, Ave, and Max temperature between the start and end date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

## Set page for precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prp_dict = {}
        prp_dict["Date"] = date
        prp_dict["Precipitation"] = prcp
        precipitation.append(prp_dict)

    return jsonify(precipitation)

## Set Flask for station
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        stat_dict = {}
        stat_dict["Station"] = station
        stat_dict["Name"] = name
        stat_dict["Lat"] = lat
        stat_dict["Lon"] = lon
        stat_dict["Elevation"] = el
        stations.append(stat_dict)

    return jsonify(stations)

## Set Flask for temperature
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

## Set Flask for Min, Ave, and Max temperature based on the start date
@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

## Set Flask for Min, Ave, and Max temperature based on the start and end date
@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

if __name__ == '__main__':
    app.run(debug=True)