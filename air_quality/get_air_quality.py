#!/usr/bin/env python3
#
# Originally:
# https://github.com/kaiterra/api/examples/restv1-urlkey.py
# 
# Adapted/updated 12-2020 by Eric Relson
#
# This script demonstrates getting the latest data from a Laser Egg and Sensedge using the API.
#
# To use the script, do the following:
#  1. Use pip to install packages in requirements.txt (usually pip -r requirements.txt)
#  2. Change API_KEY to the key you created for your Kaiterra account on http://dashboard.kaiterra.cn/.
#  3. Run the script.  It will make the request, printing out information about the auth process
#     along the way.

from datetime import datetime, timezone
from time import sleep
import os
import requests
import sys


API_BASE_URL = "https://api.kaiterra.cn/v1/"

# TODO: replace this with the API key from your Kaiterra account
API_KEY = os.getenv("KAITERRA_KEY", "OR_PUT_KEY_HERE")
LASER_EGG_SERIAL1 = os.getenv("LASEREGG_SERIAL1", "OR_PUT_KEY_HERE")

# Create a session object to reuse TCP connections to the server
session = requests.session()

def do_get(relative_url, *, params={}, headers={}):
    '''
    Executes an HTTP GET against the given resource.  The request is authorized using the given URL key.
    '''
    import json

    params['key'] = API_KEY

    url = API_BASE_URL.strip("/") + relative_url

    print("http: Fetching:   {}".format(url))
    print("http: Parameters: {}".format(params))
    print("http: Headers:  {}".format(headers))
    print()
    
    response = session.get(url, params=params, headers=headers)
    
    print("http: Status ({}), {} bytes returned:".format(response.status_code, len(response.content)))
    content_str = ''
    if len(response.content) > 0:
        content_str = response.content.decode('utf-8')
        print(content_str)
        print()

    response.raise_for_status()
        
    if len(content_str) > 0:
        return json.loads(content_str)

    return None


def get_laser_egg(id: str):
    return do_get("/lasereggs/" + id)


def get_sensedge(id: str):
    return do_get("/sensedges/" + id)


def calculate_aqi_from_pm(data):
    # Parameters from: https://forum.airnowtech.org/t/the-aqi-equation/169
    # Piecewise values for interpolating between
    levels = ["Good", "Moderate", "Unhealthy (sens)", "Unhealthy", "Very Unhealthy", "Hazardous"]
    pm25 = [[0,54, 0,50], [55,154, 51,100], [155,254, 101,150], [255,354, 151,200], [355,424, 201,300], [425,604, 301,500]]
    pm10 = [[0,12, 0,50], [12.1,35.4, 51,100], [35.5, 55.4, 101,150], [55.5,150.4, 151,200], [150.5,250.4, 201,300], [250.5,500.4, 301,500]]
    # Find interval and interpolate between AQI values in that interval
    aqi25 = "UNDEFINED"
    aqi10 = "UNDEFINED"
    for interval, name in zip(pm25, levels):
        if data["pm25"] <= interval[1]:
            aqi25 = interval[2] + (data["pm25"] - interval[0]) / (interval[1] - interval[0]) * (interval[3] - interval[2])
            level25 = name
            break
    for interval, name in zip(pm10, levels):
        if data["pm10"] <= interval[1]:
            aqi10 = interval[2] + (data["pm10"] - interval[0]) / (interval[1] - interval[0]) * (interval[3] - interval[2])
            level10 = name
            break
    aqivals = [[aqi25, level25], [aqi10, level10]]
    aqivals.sort()
    aqi, level = aqivals[-1]
    return round(aqi), level


def summarize_laser_egg(id: str):
    """
    Prints the most recently reported reading from a Laser Egg.
    """
    data = get_laser_egg(id)

    latest_data = data.get('info.aqi')
    if latest_data:
        #print("Laser Egg data returned:")

        ts = parse_rfc3339_utc(latest_data['ts'])
        ts_ago = (datetime.now(timezone.utc) - ts).total_seconds()
        #print("  Updated: {} seconds ago".format(int(ts_ago)))

        #pm25 = latest_data['data'].get('pm25')
        #if pm25:
        #    print("  PM2.5:   {} µg/m³".format(pm25))
        #else:
        #    print("  PM2.5:   no data")
        #print(data)
        for key in latest_data['data']:
            print(key, latest_data['data'][key])
        try:
            print("AQI: {0} ({1})".format(*calculate_aqi_from_pm(latest_data['data'])))
        except KeyError:
            print("Failed to get AQI from the data; missing key")
    else:
        print("Laser Egg hasn't uploaded any data yet")

    print()


def laser_egg_aqi_to_html(id: str):
    """
    Print AQI to an HTML snippet file, to be embedded in a full page's HTML.
    """
    try:
        data = get_laser_egg(id)

        latest_data = data.get('info.aqi')
    except Exception as e:
        print("Failed to get data:", e)
        return
    if latest_data:
        #print("Laser Egg data returned:")

        ts = parse_rfc3339_utc(latest_data['ts'])
        ts_ago = (datetime.now(timezone.utc) - ts).total_seconds()
        #print("  Updated: {} seconds ago".format(int(ts_ago)))

        #pm25 = latest_data['data'].get('pm25')
        #if pm25:
        #    print("  PM2.5:   {} µg/m³".format(pm25))
        #else:
        #    print("  PM2.5:   no data")
        #print(data)
        try:
            results = calculate_aqi_from_pm(latest_data['data'])
            print(results)
            with open("aqi.html", 'w') as fw:
                fw.write("Indoor AQI:<br>{0} ({1})".format(*results))
        except KeyError as e:
            print(e)
            with open("aqi.html", 'w') as fw:
                fw.write("Indoor AQI:<br>-- No Data --")
    else:
        print("Laser Egg hasn't uploaded any data yet")

    print()


def check_available(name):
    import importlib
    try:
        _ = importlib.import_module(name, None)
    except ImportError:
        print("Missing module '{}'.  Please run this command and try again:".format(name))
        print("   pip -r requirements.txt")
        sys.exit(1)


def parse_rfc3339_utc(ts: str) -> datetime:
    """
    Parses and returns the timestamp as a timezone-aware time in the UTC time zone.
    """
    return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


if __name__ == "__main__":
    check_available("requests")

    while True:
        #summarize_laser_egg(LASER_EGG_SERIAL1)
        laser_egg_aqi_to_html(LASER_EGG_SERIAL1)
        sleep(60)
