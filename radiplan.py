#!/usr/bin/env python

import sys, time, requests


latitude = 48.83
longitude = 9.11

influx_host = 'job4'
influx_db = 'radiplan'


def get_position(argv):
    if len(argv) > 2:
        return argv[1], argv[2]

    return latitude, longitude


def get_weather_meteofrance(lat, lon):
    url = 'https://api.open-meteo.com/v1/meteofrance'
    query = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "direct_radiation,diffuse_radiation,terrestrial_radiation",
        "daily": "sunrise,sunset",
        "timezone": "Europe/Berlin"
    }
    r = requests.get(url, query)
    r.raise_for_status()
    return r.json()


def put_weather_influx(json_weather):
    # tags, values, post influx
    pass


def main():
    lat, lon = get_position(sys.argv)
    while True:
        json_weather = get_weather_meteofrance(lat, lon)
        put_weather_influx(json_weather)
        time.sleep(360)