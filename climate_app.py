{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Step 4 - Climate App\n",
    "\n",
    "Now that you have completed your initial analysis, design a Flask api based on the queries that you have just developed.\n",
    "\n",
    "\n",
    "Use FLASK to create your routes."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func, desc\n",
    "\n",
    "from flask import Flask, jsonify"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "engine = create_engine(\"sqlite:///hawaii.sqlite\", echo = False )\n",
    "Base = automap_base()\n",
    "Base.prepare(engine, reflect = True)\n",
    "Base.classes.keys()\n",
    "Measurements = Base.classes.measurements\n",
    "Station=Base.classes.stations\n",
    "session = Session(engine)\n",
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/\")\n",
    "def welcome():\n",
    "    \"\"\"List all available api routes.\"\"\"\n",
    "    return (\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"List of the prior year's rain total:</br>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"List of the all Stations:</br>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"List of the prior year's temps:</br>\"\n",
    "        f\"/api/v1.0/tobs>\"\n",
    "        f\"List of the prior year's Min, Avg, and Max temps for a given date range:</br>\"\n",
    "        f\"/api/v1.0/<start><br/>\"\n",
    "        f\"/api/v1.0/<start>/<end><br/>\"\n",
    "    )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Routes\n",
    "\n",
    "/api/v1.0/precipitation\n",
    "\n",
    "* Query for the dates and temperature observations from the last year.\n",
    "* Convert the query results to a Dictionary using date as the key and tobs as the value.\n",
    "* Return the json representation of your dictionary."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    \"\"\"Return a list of rain fall for the previous year\"\"\"\n",
    "    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)\n",
    "    rain = session.query(Measurements.date,Measurements.prcp).filter\\\n",
    "    (Measurements.date>last_year).order_by(Measurements.date).all()\n",
    "\n",
    "    rain_total = []\n",
    "    for rresult in rain:\n",
    "        row={}\n",
    "        row[\"date\"] = rain[0]\n",
    "        row[\"prcp\"] = rain[1]\n",
    "        rain_totals.append(row)\n",
    "    return jsonify(rain_totals)\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Return a json list of stations from the dataset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    stations_query = session.query(Station.name, Station.station)\n",
    "    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)\n",
    "    return jsonify(stations.to_dict())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "* Return a json list of Temperature Observations (tobs) for the previous year"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    \"\"\"Return a list of dates and temps for the previous year\"\"\"\n",
    "    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)\n",
    "    temperature = session.query(Measurements.date,Measurements.tobs).filter\\\n",
    "    (Measurements.date>last_year).order_by(Measurements.date).all()\n",
    "    temperature_totals = []\n",
    "    for tresult in temperature:\n",
    "        row = {}\n",
    "        row[\"date\"] = temperature[0]\n",
    "        row[\"tobs\"] = temperature[1]\n",
    "        temperature_totals.append(row)\n",
    "    return jsonify(temperature_totals)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "* Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.\n",
    "\n",
    "* When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.\n",
    "\n",
    "* When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>\")\n",
    "def date1(start):\n",
    "    start_date = dt.datetime.strptime(start, '%Y-%M-%D')\n",
    "    last_year = dt.timedelta(days = 365)\n",
    "    start = start_date - last_year\n",
    "    end = dt.date(2017,8,23)\n",
    "    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\\\n",
    "        filter(Measurements.dat >= start).filter(Measurements.date <= end).all()\n",
    "    trip = list(np.ravel(trip_data))\n",
    "    return jsonify(trip)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def date2(start,end):\n",
    "    start_date= dt.datetime.strptime(start, '%Y-%M-%D')\n",
    "    end_date= dt.datetime.strptime(end,'%Y-%M-%D')\n",
    "    last_year = dt.timedelta(days=365)\n",
    "    start = start_date-last_year\n",
    "    end = end_date-last_year\n",
    "    trip_data = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\\\n",
    "        filter(Measurements.date >= start).filter(Measurements.date <= end).all()\n",
    "    trip = list(np.ravel(trip_data))\n",
    "    return jsonify(trip)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [
    {
     "ename": "UnsupportedOperation",
     "evalue": "not writable",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mUnsupportedOperation\u001b[0m                      Traceback (most recent call last)",
      "\u001b[1;32m<ipython-input-14-38f181c81969>\u001b[0m in \u001b[0;36m<module>\u001b[1;34m()\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[1;32mif\u001b[0m \u001b[0m__name__\u001b[0m \u001b[1;33m==\u001b[0m \u001b[1;34m\"__main__\"\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m----> 2\u001b[1;33m     \u001b[0mapp\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mrun\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mport\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;36m3000\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mdebug\u001b[0m\u001b[1;33m=\u001b[0m\u001b[1;32mTrue\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;32mC:\\ProgramData\\Anaconda3\\lib\\site-packages\\flask\\app.py\u001b[0m in \u001b[0;36mrun\u001b[1;34m(self, host, port, debug, load_dotenv, **options)\u001b[0m\n\u001b[0;32m    936\u001b[0m         \u001b[0moptions\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0msetdefault\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'threaded'\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;32mTrue\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    937\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 938\u001b[1;33m         \u001b[0mcli\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mshow_server_banner\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0menv\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mdebug\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mname\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;32mFalse\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    939\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    940\u001b[0m         \u001b[1;32mfrom\u001b[0m \u001b[0mwerkzeug\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mserving\u001b[0m \u001b[1;32mimport\u001b[0m \u001b[0mrun_simple\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32mC:\\ProgramData\\Anaconda3\\lib\\site-packages\\flask\\cli.py\u001b[0m in \u001b[0;36mshow_server_banner\u001b[1;34m(env, debug, app_import_path, eager_loading)\u001b[0m\n\u001b[0;32m    627\u001b[0m             \u001b[0mmessage\u001b[0m \u001b[1;33m+=\u001b[0m \u001b[1;34m' (lazy loading)'\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    628\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 629\u001b[1;33m         \u001b[0mclick\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mecho\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mmessage\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    630\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    631\u001b[0m     \u001b[0mclick\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mecho\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m' * Environment: {0}'\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mformat\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0menv\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32mC:\\ProgramData\\Anaconda3\\lib\\site-packages\\click\\utils.py\u001b[0m in \u001b[0;36mecho\u001b[1;34m(message, file, nl, err, color)\u001b[0m\n\u001b[0;32m    257\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    258\u001b[0m     \u001b[1;32mif\u001b[0m \u001b[0mmessage\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 259\u001b[1;33m         \u001b[0mfile\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mwrite\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mmessage\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    260\u001b[0m     \u001b[0mfile\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mflush\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    261\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;31mUnsupportedOperation\u001b[0m: not writable"
     ]
    }
   ],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    app.run(port = 3000, debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
