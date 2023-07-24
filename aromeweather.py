#!/usr/bin/env python3

import sys, time, json, requests, dateutil.parser as dp


latitude = 48.83
longitude = 9.11

influx_host = 'job4'
influx_port = 8086
influx_db = 'aromeweather'


def get_positions(argv):
    # parse commandline like lat,lon lat,lon -1 lat,lon --one-shot lat,lon lat,lon
    # return tuple of lat,lon list and oneshot flag
    locs = []
    oneShot = False
    for arg in argv[1:]:
        if arg == '-1' or arg == '--one-shot':
            oneShot = True
        else:
            try:
                locs.append((arg.split(',', 2)))
            except ValueError:
                print(f"ignoring parameter '{arg}'. Expected 'lat,lon'")

    if len(locs) == 0:
        locs.append((latitude,longitude))

    return locs, oneShot


def get_weather_meteofrance(lat, lon, days=None):
    url = 'https://api.open-meteo.com/v1/meteofrance'
    query = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relativehumidity_2m,dewpoint_2m,precipitation,snowfall,weathercode,pressure_msl,surface_pressure,cloudcover,et0_fao_evapotranspiration,vapor_pressure_deficit,windspeed_10m,winddirection_10m,windgusts_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_hours,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration",
        "timezone": "Europe/Berlin"
    }
    if days is not None:
        query["past_days"] = days  # api max days: 92
    r = requests.get(url, query)
    r.raise_for_status()
    return r.json()


def put_table_influx(pos, name, table):
    url = f"http://{influx_host}:{influx_port}/write"
    query = {
        "db": influx_db,
        "precision": "h"
    }
    lat, lon = pos
    count = 0
    for index, _ in enumerate(table["time"]):
        try:
            line = f"{name},lat={lat:.2f},lon={lon:.2f}"
            sep = " "
            for key in table.keys():
                data = table[key][index]
                if key == "time":
                    parsed_t = dp.parse(data)
                    t_in_hours = int(parsed_t.timestamp() // 3600)
                else:
                    if data is not None:
                        if type(data) is int or type(data) is float:
                            line += f"{sep}{key}={data}"
                        else:
                            line += f'{sep}{key}="{data}"'
                        sep = ","
            line += f" {t_in_hours}"
            r = requests.post(url, params=query, data=line)
            r.raise_for_status()
            count += 1
        except Exception as e:
            print(e)
    return count


def put_weather_influx(json_weather):
    # hourly_units = json_weather["hourly_units"]
    # daily_units = json_weather["daily_units"]
    pos = (json_weather["latitude"], json_weather["longitude"])
    h = put_table_influx(pos, "hourly", json_weather["hourly"])
    d = put_table_influx(pos, "daily", json_weather["daily"])
    print(f"InfluxDB updated {h} hours and {d} days for {pos}")


def main():
    # TODO process list of (lat,lon) tuples
    locs, oneshot = get_positions(sys.argv)
    if oneshot:
        for lat, lon in locs:
            json_weather = get_weather_meteofrance(lat, lon, days=92)
            put_weather_influx(json_weather)
            # print(json.dumps(json_weather, indent=2, ensure_ascii=False))
        return

    while True:
        for lat, lon in locs:
            json_weather = get_weather_meteofrance(lat, lon)
            put_weather_influx(json_weather)
        # Rate limit requests
        time.sleep(3600)


if __name__ == "__main__":
    main()
