<p align="center">
  <img src="docs/perun-weather-icon-512.png" alt="Perun Weather icon" width="128">
</p>

<h1 align="center">Perun Weather</h1>
<p align="center">Version 5.1.0</p>
<p align="center"><em>Weather, made visible.</em></p>

Perun Weather is a desktop weather application built around interactive charts.
Instead of icons and a handful of numbers, it shows how forecast variables
develop over time, so you can read the data yourself and judge what it means.

![Perun Weather main window](https://github.com/user-attachments/assets/5287dd61-9f85-442d-96af-31e7243cb404)


## Features

- Weather-at-a-glance overview: current conditions, wind compass, precipitation,
  UV, cloud cover, sun and moon, air quality, pollen and alerts on one screen
- 5-day outlook with switchable views (temperature, precipitation, wind, cloud
  cover, UV and air quality)
- Interactive forecast charts (meteograms) for temperature, UV index,
  precipitation, cloud cover, wind and pressure
- Official weather alerts worldwide, wherever official sources are available,
  with a four-level severity indicator (neutral, yellow, orange, red)
- Air quality: selectable European or US AQI, particulate matter, reactive gases,
  dust and aerosol optical depth
- Pollen forecast
- Sun and moon data: altitude, day and night, moon visibility and daily summary
- Optional marine panel
- Expanded choice of global and European weather models, including ECMWF IFS/AIFS,
  GFS/AIGFS, JMA, ICON, GEM, ARPEGE, UK Met Office, CMA, HARMONIE and CHMI ALADIN,
  plus Best match and fallback when the selected model has no usable data
- Save as many locations as you like and reorder them by dragging
- Add locations by name or by entering coordinates
- Selectable time step (1, 3 or 6 hours) and forecast range
  (3, 5, 7 or 16 days)
- Five unit presets (metric, mmHg, imperial, m/s and knots variants)
- Adjustable line smoothing, from raw data to strong smoothing
- Automatic refresh with a last-updated indicator
- Collapsible settings for model, units, air quality scale, panels and chart options
- Slovak and English interface
- Weather maps with WeatherAPI.com layer selection and an alternative
  Xweather radar source, animation and frame selection
- Built-in Slovak and English help, including map setup and limitations


## Weather maps

Enable the map panel in Settings and expand it to load the map.
Choose WeatherAPI.com or Xweather using the source selector.

- WeatherAPI.com is the default for new settings. Existing saved source
  selections are preserved. Use the layer selector to choose a weather layer.
- Xweather requires your own Client ID and Client Secret. In the Xweather
  portal, open [Account → Keys](https://data.portal.xweather.com/account/keys),
  create an application and copy its credentials into the application settings.
  The combined `ID_SECRET` string can also be pasted into the first field.
  Access and usage limits depend on your plan.
- Use the play button and time slider to animate or select map frames.
  The displayed map time is separate from the forecast chart timeline.
- WeatherAPI.com layer legends are currently hidden. Do not interpret map
  colours using forecast chart scales or another provider's legend.
- Credentials are stored in the application settings on your computer.
  Do not include them in public screenshots, bug reports or commits.

Map sources are separate from the Open-Meteo forecast model used in the charts.
Missing tiles or frames do not mean that there is no precipitation.
Maps supplement forecasts and official warnings; they do not replace them.

## Release notes

Version 5.1.0 · 2026-10-19:
[Release notes](docs/release-notes-5.1.0.md)

## Screenshots

**Alerts**

![Alerts](https://github.com/user-attachments/assets/b3091239-68c4-4194-b2e5-832a1b677e4a)


**Air quality & pollen**

![Air quality and pollen](https://github.com/user-attachments/assets/fb7e90d5-4771-4843-80cb-ce6c84fae3f3)


**Weather forecast**

![Weather forecast](https://github.com/user-attachments/assets/62ba819a-e69c-4ce9-88c0-4f272bfc32dc)


**Sun & moon**

![Sun and moon](https://github.com/user-attachments/assets/2ec51210-072f-4efe-b3f0-c6f90065dfbc)


**Marine panel (optional)**

![Marine data](https://github.com/user-attachments/assets/b1f377d1-1143-4ffc-bd41-36787f9c1515)


**Settings**

![Settings](https://github.com/user-attachments/assets/dd0efebd-537e-433c-a518-136a77cfe3b4)


**Help**

![Help](https://github.com/user-attachments/assets/5b91b136-05cb-44d0-a698-a0cc67dace96)


## About the name

Perun is the highest god of the early Medieval Slavic pantheon, the lord of the
sky, thunder, lightning and storms. He was also associated with rain, fertility
and the oak, and his symbols included fire, wind, mountains, the eagle and the
thunder axe.

The name seemed fitting for an application that follows storms, rain and wind
through the data. It refers only to the mythological figure and has no political or religious meaning.

*Source: [Perun on Wikipedia](https://en.wikipedia.org/wiki/Perun).*

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
sudo dnf install ./perun-weather-5.1.0-1.fc44.noarch.rpm
```

`dnf` installs the required dependencies automatically.

### Debian (DEB)

Download the latest `.deb` from the [Releases](https://github.com/tothpsk/perun-weather/releases)
page and install it:

```bash
sudo apt install ./perun-weather_5.1.0-1_all.deb
```

Use `apt install` with the `./` prefix rather than `dpkg -i`, so that `apt`
installs the dependencies for you. On a minimal system this pulls in a large
number of packages, mostly because of WebKitGTK and its media libraries.

Built and tested on Debian 13 (trixie). Other Debian-based distributions may
work but are untested; the application requires Python 3.12 or newer.

### Windows

Download the Windows ZIP from [Releases](https://github.com/tothpsk/perun-weather/releases),
extract the whole folder and run `PerunWeather.exe`. Keep all files in the
folder together. No separate installation of Python or Qt is needed.

### Dependencies (Linux)

The Linux packages depend on:

| Component | Debian package | Fedora package |
|---|---|---|
| Python bindings for GObject | `python3-gi` | `python3-gobject` |
| GTK 4 | `gir1.2-gtk-4.0` | `gtk4` |
| libadwaita | `gir1.2-adw-1` | `libadwaita` |
| WebKitGTK 6 | `gir1.2-webkit-6.0` | `webkitgtk6.0` |

These are installed automatically with the package. You only need to install
them manually when running Perun Weather from source.

## Roadmap

Planned ideas, in no particular order:

- ~~Weather maps and radar~~ (added in 5.1.0)
- ~~Further weather models~~ (done in 4.5)
- Historical weather
- A gardening and agriculture panel (soil moisture and drought information
  for hobby growers and professional farmers)
- Themes
- ~~.deb version~~ (done in 4.0.1)
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
  This covers forecasts, air quality and marine data. The application converts
  units and visualises the data. Underlying model data come from national
  weather services and agencies such as DWD, ECMWF, NOAA and DMI; air quality
  data come from the Copernicus Atmosphere Monitoring Service (CAMS). Please see
  the Open-Meteo licence page for the full list and terms.
- **Place search:** [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api),
  based on [GeoNames](https://www.geonames.org/) (CC BY 4.0).
- **Place names for coordinates:** [Nominatim](https://nominatim.openstreetmap.org/),
  © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (ODbL).
- **Official warnings:**
  - [MeteoAlarm](https://feeds.meteoalarm.org): official warnings for Europe,
    aggregated from national meteorological services.
  - [FOSS Public Alert Server](https://github.com/KDE/foss-public-alert-server)
    ([alerts.kde.org](https://alerts.kde.org)): official CAP warnings collected
    from alerting authorities worldwide, a project of KDE and the FOSS Warn team.
- **Charts:** [Plotly.js](https://plotly.com/javascript/) (MIT License), bundled
  locally with the application.

### Maps and map rendering

- Weather map layers: [WeatherAPI.com](https://www.weatherapi.com/),
  when selected. Provider terms apply.
- Alternative radar imagery:
  [Powered by Vaisala Xweather](https://www.xweather.com/).
  Requires user-supplied credentials and an appropriate service plan.
- Interactive map rendering: [Leaflet 1.9.4](https://leafletjs.com/),
  bundled locally, under the
  [BSD-2-Clause license](perun_weather/data/leaflet-LICENSE.txt).
  Leaflet is a software library, not a weather data provider.

Map data, map backgrounds and software libraries have separate terms.
Provider credits displayed on the map must be preserved.

### Usage note

The free Open-Meteo API is intended for non-commercial use
([Terms](https://open-meteo.com/en/terms)). If you run a public deployment with
advertising, subscriptions or other commercial use, you need a commercial
Open-Meteo plan.

Weather data may contain errors or omissions. Do not rely on this application as
the only source for safety-critical decisions; consult official warnings.
