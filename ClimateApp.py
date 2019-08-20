
import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


####FLASK Setup####
app = Flask(__name__)

####DATES####
lastdatadt =  session.query(Measurement.date).order_by(Measurement.date.desc()).first()
lastdatadt = list(np.ravel(lastdatadt))[0]
lastdatadt = dt.datetime.strptime(lastdatadt, '%Y-%m-%d')
Year = int(dt.datetime.strftime(lastdatadt, '%Y'))
Month = int(dt.datetime.strftime(lastdatadt, '%m'))
Day = int(dt.datetime.strftime(lastdatadt, '%d'))
yearbeforedt = dt.date(Year, Month, Day) - dt.timedelta(days = 365)
yearbeforedt = dt.datetime.strftime(yearbeforedt, '%Y-%m-%d')

####All FLASK Routes####
@app.route("/")
def home():
    return(
        f"<center>"
        f"<strong>Welcome to Climate App</strong><br>"
        f"<b>Available Routes:</b><br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

####Precipitation#####
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    precipitationq = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= yearbeforedt).all()

    session.close()

    precipitationq_list=[]
    for data in precipitationq:
        precipitation_dict = {data.date: data.prcp}
        precipitationq_list.append(precipitation_dict)
    
    return jsonify( precipitationq_list)
    

####Stations####
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stationsquery= session.query(Station.name).all()

    session.close()

    stationlist=list(np.ravel(stationsquery))

    return jsonify(stationlist)

    ########OR########

    # session = Session(engine)

    # stationsquery= session.query(Station.name, Station.station, Station.latitude, Station.longitude, Station.elevation).all()

    # session.close()

    # stationslist = []
    # for name, station, latitude, longitude, elevation in stationsquery:
    #     stations_dict = {}
    #     stations_dict['name'] = name
    #     stations_dict['station'] = station
    #     stations_dict['latitude'] = latitude
    #     stations_dict['longitude'] = longitude
    #     stations_dict['elevation'] = elevation
    #     stationslist.append(stations_dict)

    #return jsonify(stationslist)
    

####Temp####
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    tobsquery = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= yearbeforedt).order_by(Measurement.date.desc()).all()

    session.close()

    #tobslist=list(np.ravel(tobsquery))

    tobs_year_info=[]
    for date, tobs in tobsquery:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_year_info.append(tobs_dict)
    
    return jsonify(tobs_year_info)

####MIN MAX AVG Temp by date####
@app.route("/api/v1.0/<start>")
def star_temp(start):
    session = Session(engine)

    startdate_query= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    start_dict= []
    for min_temp, max_temp, avg_temp in startdate_query:
        search_date = {}
        search_date['Min Temp'] = min_temp   
        search_date['Max Temp'] = max_temp
        search_date['Avg Temp'] = avg_temp
        start_dict.append(search_date)

    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def end_temp(start, end):

    session = Session(engine)

    startend_query= session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    startend_dict= []
    for min_temp, max_temp, avg_temp in startend_query:
        search_date2 = {}
        search_date2['Min Temp'] = min_temp   
        search_date2['Max Temp'] = max_temp
        search_date2['Avg Temp'] = avg_temp
        startend_dict.append(search_date2)

    return jsonify(startend_dict)

if __name__ == "__main__":
    app.run()