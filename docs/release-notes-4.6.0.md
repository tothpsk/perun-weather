# Perun Weather 4.6.0

Weather, made visible: interactive charts for forecasts, air quality, pollen,
sun and moon data, optional marine data and official weather alerts, powered
by Open-Meteo.

## What's new

- Added a precipitation probability strip below the precipitation and cloud cover chart, where colour intensity shows probability; the value is also shown in the weather summary.
- Applied readable five-tick axes with outward ticks to forecast, air quality, pollen and marine charts; non-negative data start at zero, cloud cover stays at 0–100 %, and UV starts at zero.
- The temperature axis now follows the visible minimum and maximum with readable values.
- Tuned marine charts, including finer one-decimal tide steps, and removed the wave-direction entry from the legend while keeping the arrows.
- Fixed duplicate dates and doubled day dividers when daylight-saving time changes.
- Kept the same spacing below charts for every forecast range and unified tooltip typography.

## Downloads

| Platform | File |
|---|---|
| Fedora 44 (RPM) | `perun-weather-4.6.0-1.fc44.noarch.rpm` |
| Debian 13 (DEB) | `perun-weather_4.6.0-1_all.deb` |
| Windows | `PerunWeather-4.6.0-windows.zip` |

## Installation

### Fedora

```bash
sudo dnf install ./perun-weather-4.6.0-1.fc44.noarch.rpm
```

### Debian

```bash
sudo apt install ./perun-weather_4.6.0-1_all.deb
```

Use `apt install` with the `./` prefix so that dependencies are installed automatically.

### Windows

Extract the whole ZIP folder and run `PerunWeather.exe`. Keep all files in the folder together. No separate installation of Python or Qt is needed.

## Requirements (Linux)

Python 3.12 or newer, GTK 4, libadwaita and WebKitGTK 6.

Dependencies are installed automatically with the package.

Full changelog: [v4.5.1...v4.6.0](https://github.com/tothpsk/perun-weather/compare/v4.5.1...v4.6.0)
