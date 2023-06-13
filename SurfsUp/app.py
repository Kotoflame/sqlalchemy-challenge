# Import the dependencies.
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
from datetime import datetime,timedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    "Here are all available api routes."
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>   in the form YYYYMMDD"
        "/api/v1.0/<start>/<end>   in the form YYYYMMDD/YYYYMMDD"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    newestday = session.query(measurement).order_by(measurement.date.desc()).first().date
    DTnewestday = datetime.strptime(newestday,"%Y-%m-%d")
    
    # Calculate the date one year from the last date in data set.
    oneYrs = DTnewestday - timedelta(days = 366)
    
    """Collect precipitation data for the last 12 months."""
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date >= oneYrs).order_by(measurement.date).all()
    
    #create a dictionary to hold results
    resDict = {}
    for date,prcp in results:
        resDict[date] = prcp
    session.close()

    return jsonify(resDict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #perform a query for all stations
    stationlist = session.query(station.station).all()
    
    session.close()
    all_stations = list(np.ravel(stationlist))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #calculate the most recent date available
    newestday = session.query(measurement).order_by(measurement.date.desc()).first().date
    DTnewestday = datetime.strptime(newestday,"%Y-%m-%d")
    
    #calculate the date on year prior to the most recent available
    oneYrs = DTnewestday - timedelta(days = 366)

    #query the dates and temperatures for the specified station and date range.
    stationresults = session.query(measurement.date,measurement.tobs).filter(measurement.date >= oneYrs).filter(measurement.station == 'USC00519281').all()

    #arrange output
    resDict = {}
    for date,tobs in stationresults:
        resDict[date] = tobs
        
    session.close()
 
    return jsonify(resDict)

@app.route("/api/v1.0/<start>")
def tempstats(start):
    # assume input of the form YYYYMMDD
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #format the start date from the expected form
    startdate = datetime.strptime(start,'%Y%m%d')
        
    #query for the desired statistics
    statresults = session.query(func.min(measurement.tobs),
                      func.avg(measurement.tobs),
                      func.max(measurement.tobs))\
                .filter(measurement.station == 'USC00519281')\
                .filter(measurement.date >= startdate).all()
    
    #arrange output
    resDict = {}
    for minval,avg,maxval in statresults:
        resDict['min'] = minval
        resDict['avg'] = avg
        resDict['max'] = maxval

    
    session.close()
    
    return jsonify(resDict)

@app.route("/api/v1.0/<start>/<end>")
def tempstatsB(start,end):
    # assume input of the form YYYYMMDD
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #format the start and end dates from the expected form
    startdate = datetime.strptime(start,'%Y%m%d')
    enddate = datetime.strptime(end,'%Y%m%d')
  
    #query for the desired statistics, with the end filter dates
    statresults = session.query(func.min(measurement.tobs),
                      func.avg(measurement.tobs),
                      func.max(measurement.tobs))\
                    .filter(measurement.station == 'USC00519281')\
                    .filter(measurement.date >= startdate)\
                    .filter(enddate >= measurement.date).all()
    
    #arrange output       
    resDict = {}
    for minval,avg,maxval in statresults:
        resDict['min'] = minval
        resDict['avg'] = avg
        resDict['max'] = maxval
   
    session.close()
    return jsonify(resDict)

if __name__ == '__main__':
    app.run(debug=True)
