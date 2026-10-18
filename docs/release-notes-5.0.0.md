# Perun Weather 5.0.0

Weather, made visible: a new overview screen, a 5-day outlook and a reorganised settings panel on top of interactive charts for forecasts, air quality, pollen, sun and moon data, the optional marine panel and official weather alerts, powered by Open-Meteo.

## What's new

- A new "Weather at a glance" overview shows current conditions, wind with a direction compass, precipitation, UV, cloud cover, sun and moon, air quality, pollen and alerts on one screen.
- A 5-day outlook with switchable views: temperature, precipitation, wind, cloud cover, UV and air quality.
- The detailed sections (alerts, air quality and pollen, weather forecast, sun and moon) start collapsed and keep their key values visible in the header.
- A collapsible Settings section groups Data (forecast model, units, air quality scale), Panels (Marine panel on or off) and Charts (forecast range, time interval, line smoothing).
- Refresh and auto-refresh controls moved into the header next to the language switch.
- Marine data is now called Marine panel.
- Wind direction text now reads "from NW" in English and "z SZ" or "zo SZ" in Slovak, using Slovak abbreviations.
- Decimal numbers use a dot, and temperatures have no space before the degree sign.

## Downloads

| Platform | File |
|---|---|
| Fedora 44 (RPM) | `perun-weather-5.0.0-1.fc44.noarch.rpm` |
| Debian 13 (DEB) | `perun-weather_5.0.0-1_all.deb` |
| Windows | `PerunWeather-5.0.0-windows.zip` |

## Installation

### Fedora

```bash
sudo dnf install ./perun-weather-5.0.0-1.fc44.noarch.rpm
```

### Debian

```bash
sudo apt install ./perun-weather_5.0.0-1_all.deb
```

Use `apt install` with the `./` prefix so that dependencies are installed automatically.

### Windows

Extract the whole ZIP folder and run `PerunWeather.exe`. Keep all files in the folder together. No separate installation of Python or Qt is needed.

## Requirements (Linux)

Python 3.12 or newer, GTK 4, libadwaita and WebKitGTK 6.

Dependencies are installed automatically with the package.

Full changelog: [v4.6.0...v5.0.0](https://github.com/tothpsk/perun-weather/compare/v4.6.0...v5.0.0)
