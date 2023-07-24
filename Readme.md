# Arome Weather

Read MeteoFrance API for Arome weather forecast and put result into influx database

Could be used e.g. in Grafana like this:

![grafik](https://github.com/joba-1/AromeWeather/assets/32450554/8363abbe-d9eb-49a4-a588-c07862e1891e)

## Documentation

* [MeteoFrance API Request](https://api.open-meteo.com/v1/meteofrance?latitude=48.83&longitude=9.11&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,precipitation,snowfall,weathercode,pressure_msl,surface_pressure,cloudcover,et0_fao_evapotranspiration,vapor_pressure_deficit,windspeed_10m,winddirection_10m,windgusts_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_hours,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration&timezone=Europe%2FBerlin)
* [MeteoFrance API UI](https://open-meteo.com/en/docs/meteofrance-api#latitude=48.83&longitude=9.11&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,precipitation,snowfall,weathercode,pressure_msl,surface_pressure,cloudcover,et0_fao_evapotranspiration,vapor_pressure_deficit,windspeed_10m,winddirection_10m,windgusts_10m,shortwave_radiation,direct_radiation,diffuse_radiation,direct_normal_irradiance,terrestrial_radiation&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_hours,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration&timezone=Europe%2FBerlin)

## Installation

as user joachim (or adapt service file)

```
cp aromeweather.py aromeweather.sh /home/joachim/bin/
conda create -n aromeweather python requests python-dateutil
influx -execute "create database aromeweather"
sudo cp aromeweather.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start aromeweather
sudo systemctl enable aromeweather
sudo systemctl status aromeweather
```

Add more locations by adding them to aromeweather.service ExecStart
Add same locations to influx db, so grafana can pick them up there:
```
influx -database aromeweather -precision h -execute "insert location,name=Mahlstetten lat=48.08,lon=8.83"
```
Optionally load 92 days history of a location to influx db:
```
aromeweather.py -1 49.26,8.59
```
