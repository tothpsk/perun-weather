**Perun Weather** **4**  
Added: optional marine panel — sea surface temperature, modelled sea level with next maximum/minimum, wave height, period and direction, enabled by a checkbox under the model selector  
Added: adding locations by coordinates, in addition to searching by name  
Added: worldwide official warnings through the FOSS Public Alert Server, next to MeteoAlarm and local threshold estimates  
Added: UV index supplemented from GFS where the selected model has none  
Added: phase name of the moon in the Sun & moon panel header  
Added: plain-language names for air-quality series and a glossary of abbreviations in this help  
Changed: unified tooltip layout in all charts — time, series name, value and unit, with width adapting to content  
Changed: warning header lists warning counts by event type and severity  
Changed: improved warning integration and layout of the alerts chart  
Changed: restyled "now" line; different curve color for aerosol optical depth; air-quality chart translations  
Changed: better integration of other forecast models so that they also show UV index; ECMWF AIFS is working again  
Fixed: day names and dates in the Sun & moon chart moved higher; larger font; day-length icon added; capitalisation in the Sun tooltip  
Fixed: time-zone error; wrong number of weather warnings; moon trend not synchronised with the phase  
Fixed: the header of the alerts chart (day and date) went missing when there were many warnings  
Fixed: pressure number format in the tooltip now matches the axis (e.g. 1 012 hPa)  
Fixed: wind and wave direction added to the legend; wind direction added to the wind tooltip  

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
  FOSS Public Alert Server (available global CAP sources).
- **Charts:** [Plotly.js](https://plotly.com/javascript/) (MIT License).

Open-Meteo, MeteoAlarm and the other data providers do not endorse this project.

### Usage note

The free Open-Meteo API is intended for non-commercial use
([Terms](https://open-meteo.com/en/terms)). If you run a public deployment with
advertising, subscriptions or other commercial use, you need a commercial
Open-Meteo plan.

Weather data may contain errors or omissions. Do not rely on this application as
the only source for safety-critical decisions; consult official warnings.
