#!/usr/bin/env python

import sys, time, requests, dateutil.parser as dp


latitude = 48.83
longitude = 9.11

influx_host = 'job4'
influx_port = 8086
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
        "timezone": "Europe/Berlin"
    }
    r = requests.get(url, query)
    r.raise_for_status()
    return r.json()


def put_weather_influx(json_weather):
    lat, lon = json_weather["latitude"], json_weather["longitude"]
    units = json_weather["hourly_units"]
    t_u, direct_u, diffuse_u, terrestrial_u = units["time"], units["direct_radiation"], units["diffuse_radiation"], units["terrestrial_radiation"]
    hourly = json_weather["hourly"]
    times = hourly["time"]
    directs = hourly["direct_radiation"]
    diffuses = hourly["diffuse_radiation"]
    terrestrials = hourly["terrestrial_radiation"]
    url = f"http://{influx_host}:{influx_port}/write"
    query = {
        "db": influx_db,
        "precision": "h"
    }
    print(f"@lat,lon {lat:.2f},{lon:.2f}:")
    for t, direct, diffuse, terrestrial in zip(times, directs, diffuses, terrestrials):
        print(f"{t}:  {direct:6.1f} {direct_u} direct,  {diffuse:6.1f} {diffuse_u} diffuse,  {terrestrial:6.1f} {terrestrial_u} terrestrial")

    for t, direct, diffuse, terrestrial in zip(times, directs, diffuses, terrestrials):
        if direct < 0: direct = 0.0
        if diffuse < 0: diffuse = 0.0
        if terrestrial < 0: terrestrial = 0.0
        parsed_t = dp.parse(t)
        t_in_hours = int(parsed_t.timestamp() // 3600)
        line = f"radiation,lat={lat:.2f},lon={lon:.2f} direct={direct},diffuse={diffuse},combined={direct+diffuse},terrestrial={terrestrial} {t_in_hours}"
        r = requests.post(url, params=query, data=line)
        r.raise_for_status()


def main():
    lat, lon = get_position(sys.argv)
    while True:
        json_weather = get_weather_meteofrance(lat, lon)
        put_weather_influx(json_weather)
        time.sleep(3600)


if __name__ == "__main__":
    main()
