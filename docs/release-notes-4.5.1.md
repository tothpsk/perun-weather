# Perun Weather 4.5.1

Weather, made visible: interactive charts for forecasts, air quality, pollen,
sun and moon data, optional marine data and official weather alerts, powered
by Open-Meteo.

## What's new

- Fixed the precipitation axis to start at zero, including periods without precipitation, on Linux and Windows.
- Aligned wind and pressure axes to a shared grid with readable ticks for hPa, mmHg and inHg.
- Normal pollutant and pollen values remain off-white; warning colours and the selected AQI colour scale are preserved.
- Added a bilingual tooltip explaining the air/pollen indicator and the values responsible for its colour.
- Shortened the aerosol optical depth summary label to AOD and added a matching styled explanatory tooltip.
- AQI in the indicator tooltip uses integer formatting, matching the summary; other variables retain their units and precision.
- Polished README wording and updated release metadata.

## Downloads

| Platform | File |
|---|---|
| Fedora 44 (RPM) | `perun-weather-4.5.1-1.fc44.noarch.rpm` |
| Debian 13 (DEB) | `perun-weather_4.5.1-1_all.deb` |
| Windows | `PerunWeather-4.5.1-windows.zip` |

The Windows package includes the precipitation axis fix that held back the
Windows build in version 4.5.0.

## Installation

### Fedora

```bash
sudo dnf install ./perun-weather-4.5.1-1.fc44.noarch.rpm
```

### Debian

```bash
sudo apt install ./perun-weather_4.5.1-1_all.deb
```

Use `apt install` with the `./` prefix to install dependencies automatically.

### Windows

Extract the whole ZIP folder and run `PerunWeather.exe`. Keep all files together.
No separate installation of Python or Qt is needed.

## Requirements (Linux)

Python 3.12 or newer, GTK 4, libadwaita and WebKitGTK 6.
Dependencies are installed automatically with the package.

Full changelog: [v4.5.0...v4.5.1](https://github.com/tothpsk/perun-weather/compare/v4.5.0...v4.5.1)
