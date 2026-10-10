<p align="center">
  <img src="docs/perun-weather-icon-512.png" alt="Perun Weather icon" width="128">
</p>

<h1 align="center">Perun Weather</h1>
<p align="center"><em>Weather, made visible.</em></p>

Perun Weather is a desktop weather application built around interactive charts.
Instead of icons and a handful of numbers, it shows how forecast variables
develop over time, so you can read the data yourself and judge what it means.

![Perun Weather main window](https://github.com/user-attachments/assets/58934efb-5e4a-4a6d-af40-628ff8c2c968)

## Features

- Interactive forecast charts (meteograms) for temperature, UV index,
  precipitation, cloud cover, wind and pressure
- Choice of weather models, from global (ECMWF IFS, ECMWF AIFS, GFS) to
  regional (DWD ICON D2 and ICON EU, DMI HARMONIE), plus an automatic
  best-match blend
- Selectable time step (1, 3 or 6 hours) and forecast range
  (3, 5, 7 or 16 days)
- Air quality: AQI, particulate matter, reactive gases, dust and aerosol
  optical depth
- Pollen forecast
- Sun and moon data: altitude, day and night, moon visibility and daily summary
- Optional marine data
- Official weather alerts with a four-level severity indicator
  (neutral, yellow, orange, red)
- Saved locations that you can reorder by dragging
- Five unit presets (metric, mmHg, imperial, m/s and knots variants)
- Adjustable line smoothing, from raw data to strong smoothing
- Automatic refresh with a last-updated indicator
- Slovak and English interface
- Comprehensive help


## Screenshots

**Alerts**

![Alerts](https://github.com/user-attachments/assets/81f9dc10-a9c9-4710-9b81-470ebafcdc7d)

**Air quality & pollen**

![Air quality and pollen](https://github.com/user-attachments/assets/4b1a6012-78d6-48c2-ab2e-f1fa1a7051d0)


**Sun & moon**

![Sun and moon](https://github.com/user-attachments/assets/adeb6490-ba5f-4374-bf30-c439c8853f06)


**Marine data**

![Marine data](https://github.com/user-attachments/assets/2a05e6a1-99bd-4c76-90fa-72465c253586)



## Why I made it

Perun Weather is a hobby project. There are many beautiful weather
applications on Linux, but as someone who likes data, I found their
graphics-first approach less useful than I wanted.

I work as an archaeologist, and planning fieldwork depends on understanding
the weather in detail. After experimenting with vibe coding, I decided to build
an application that fits the way I read forecasts.

## Design approach

The first draft of Perun Weather was an HTML mockup. I later experimented with
a native build for Fedora's GNOME desktop, but its look did not appeal to me.
So I decided to keep the interface as close to the original mockup as
possible, while keeping the application compatible with possible ports to
other operating systems.

For this reason the charts and much of the interface are built with web
technologies and displayed inside a native application window.

## Installation

### Fedora (RPM)

Download the latest `.rpm` from the [Releases](https://github.com/tothpsk/perun-weather/releases)
page and install it:

```bash
sudo dnf install ./perun-weather-4.0.0-1.fc44.noarch.rpm
```

### Windows

Download the Windows ZIP from [Releases](https://github.com/tothpsk/perun-weather/releases),
extract the whole folder and run `PerunWeather.exe`. Keep all files in the
folder together.

## Roadmap

Planned ideas, in no particular order:

- Weather radar
- Further weather models
- Historical weather
- A gardening and agriculture panel (soil moisture and drought information
  for hobby growers and professional farmers)
- Themes
- *.deb version
- A web version and a mobile app

## Feedback

This is a hobby project, so replies may take a while. Bug reports and ideas are
welcome in [Issues](https://github.com/tothpsk/perun-weather/issues).

## License

The source code is released under the [MIT License](LICENSE).
Data from third-party providers remains under the terms of those providers.

## Data sources and attribution

Perun Weather does not generate meteorological data. It fetches and visualises
data from the following services:

- **Weather data by [Open-Meteo.com](https://open-meteo.com/)**, licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
  ([licence details](https://open-meteo.com/en/licence)).
  This covers forecasts, air quality (based on CAMS / Copernicus) and marine data.
  The application converts units and visualises the data.
  Underlying model data come from national weather services such as DWD, ECMWF,
  NOAA and DMI; please see the Open-Meteo licence page for the full list and terms.
- **Place search:** Open-Meteo Geocoding API, based on
  [GeoNames](https://www.geonames.org/) (CC BY 4.0).
- **Official warnings:** [MeteoAlarm](https://feeds.meteoalarm.org) (Europe) and the
  [FOSS Public Alert Server (available global CAP sources)](https://github.com/KDE/foss-public-alert-server)
- **Charts:** [Plotly.js](https://plotly.com/javascript/) (MIT License).

Open-Meteo, MeteoAlarm and the other data providers do not endorse this project.

### Usage note

The free Open-Meteo API is intended for non-commercial use
([Terms](https://open-meteo.com/en/terms)). If you run a public deployment with
advertising, subscriptions or other commercial use, you need a commercial
Open-Meteo plan.

Weather data may contain errors or omissions. Do not rely on this application as
the only source for safety-critical decisions; consult official warnings.
