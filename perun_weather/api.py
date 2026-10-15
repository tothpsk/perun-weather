from __future__ import annotations
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER_AGENT = "PerunWeather/4.0 (+https://github.com/tothpsk/perun-weather)"
FORECAST = "https://api.open-meteo.com/v1/forecast"
ECMWF = "https://api.open-meteo.com/v1/ecmwf"
AIR = "https://air-quality-api.open-meteo.com/v1/air-quality"
MARINE = "https://marine-api.open-meteo.com/v1/marine"
GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_MAX_DAYS = 16
AIR_MAX_DAYS = 7

WEATHER_VARS = "temperature_2m,apparent_temperature,uv_index,rain,showers,snowfall,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_direction_10m,wind_gusts_10m,weather_code,pressure_msl"
# The dedicated /v1/ecmwf endpoint does not derive uv_index (no native or
# derived UV field is documented for IFS/AIFS); requesting it there returns
# an all-null series rather than an error, so it is omitted for that
# endpoint specifically and the UV chart/chip simply shows "not available".
ECMWF_VARS = "temperature_2m,apparent_temperature,rain,showers,snowfall,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,wind_direction_10m,wind_gusts_10m,weather_code,pressure_msl"
AIR_VARS = "european_aqi,us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ammonia,dust,aerosol_optical_depth,alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen"

# Models routed through the generic /v1/forecast endpoint's `models=` param.
GENERIC_MODEL_MAP = {
    "best_match": None,
    "icon_d2": "icon_d2",
    "icon_eu": "icon_eu",
    "gfs": "gfs_seamless",
    "harmonie": "dmi_seamless",
    "cma_grapes": "cma_grapes_global",
    "aigfs": "ncep_aigfs025",
    "jma_gsm": "jma_gsm",
    "icon_global": "dwd_icon_global",
    "gem_global": "cmc_gem_gdps",
    "arpege_world": "meteofrance_arpege_world",
    "ukmo_global": "ukmo_global_deterministic_10km",
    "arpege_europe": "meteofrance_arpege_europe",
    "knmi_arome_europe": "knmi_harmonie_arome_europe",
    "chmi_aladin_seamless": "chmi_aladin_seamless",
    "chmi_aladin_ce_2km": "chmi_aladin_central_europe_2km",
    "chmi_aladin_cz_1km": "chmi_aladin_cz_1km",
    "icon_seamless": "dwd_icon_seamless",
}

# Models that must be routed through the dedicated /v1/ecmwf endpoint
# instead of the generic multi-model /v1/forecast endpoint. Open-Meteo's
# generic endpoint does not correctly resolve these model IDs (it silently
# returns an all-null hourly series instead of an error), while the
# dedicated ECMWF endpoint natively supports them and auto-interpolates
# their native 3-/6-hourly data to a consistent 1-hourly series.
ECMWF_MODEL_MAP = {
    "ecmwf_ifs_hres": None,   # HRES uses models=ecmwf_ifs on /v1/forecast
    "ecmwf_ifs": "ecmwf_ifs025",
    "ecmwf_aifs": "ecmwf_aifs025_single",
}

MODEL_LABELS = {
    "best_match": "Best match (auto-blend)",
    "icon_d2": "ICON D2 (DWD, 2 km, Europe)",
    "icon_eu": "ICON EU (DWD, 7 km, Europe)",
    "ecmwf_ifs_hres": "ECMWF IFS HRES (9 km, global)",
    "ecmwf_ifs": "ECMWF IFS 0.25° (global, 3-6h native)",
    "ecmwf_aifs": "ECMWF AIFS (AI model, global, 6h native)",
    "gfs": "GFS (NOAA, global)",
    "harmonie": "DMI Seamless (HARMONIE → ECMWF, Europe)",
    "cma_grapes": "CMA GRAPES (global)",
    "aigfs": "NCEP AIGFS (AI model, global)",
    "jma_gsm": "JMA GSM (global)",
    "icon_global": "ICON Global (DWD, global)",
    "gem_global": "GEM Global (Canada, global)",
    "arpege_world": "ARPEGE World (Météo-France, global)",
    "ukmo_global": "UK Met Office Global (10 km, global)",
    "arpege_europe": "ARPEGE Europe (Météo-France, Europe)",
    "knmi_arome_europe": "HARMONIE AROME Europe (KNMI, Europe)",
    "chmi_aladin_seamless": "CHMI ALADIN Seamless (ALADIN → ECMWF, Central Europe)",
    "chmi_aladin_ce_2km": "CHMI ALADIN Central Europe (2 km)",
    "chmi_aladin_cz_1km": "CHMI ALADIN CZ (1 km, Czechia)",
    "icon_seamless": "ICON Seamless (DWD, Global + EU + D2)",
}

# UV index is not available at all via the dedicated ECMWF endpoint.
ECMWF_MODELS = set(ECMWF_MODEL_MAP.keys())


class NoModelData(RuntimeError):
    """Raised when a weather model returns no usable data for a location."""


class ApiRequestError(RuntimeError):
    """HTTP or network failure while calling an API."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


MESSAGES = {
    "en": {
        "europe_only": "{model} is only available in Europe. Switched to Best match.",
        "no_data": "{model} has no data for {place}. Switched to Best match.",
        "no_data_final": "No forecast data is available for {place}.",
        "request_failed": "Could not load data from Open-Meteo. Check your connection and try again.",
    },
    "sk": {
        "europe_only": "Model {model} je dostupný len v Európe. Prepnuté na Best match.",
        "no_data": "Model {model} nemá dáta pre lokalitu {place}. Prepnuté na Best match.",
        "no_data_final": "Pre lokalitu {place} nie sú dostupné dáta predpovede.",
        "request_failed": "Nepodarilo sa načítať dáta z Open-Meteo. Skontroluj pripojenie a skús to znova.",
    },
}


def msg(lang: str, key: str, **values) -> str:
    table = MESSAGES.get(lang) or MESSAGES["en"]
    return table[key].format(**values)


def request(url: str, parameters: dict) -> dict:
    req = Request(url + "?" + urlencode(parameters), headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        raise ApiRequestError(f"API request failed: {e}", e.code)
    except Exception as e:
        raise ApiRequestError(f"API request failed: {e}")


def geocode(query: str) -> list[dict]:
    """Search for locations."""
    data = request(GEOCODE, {"name": query, "count": 8, "language": "en", "format": "json"})
    return data.get("results", [])

REVERSE_GEOCODE = "https://nominatim.openstreetmap.org/reverse"

def reverse_geocode(lat: float, lon: float) -> dict | None:
    """Return location metadata for coordinates, or None if lookup fails."""
    try:
        data = request(REVERSE_GEOCODE, {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
            "zoom": 10,
            "addressdetails": 1,
            "accept-language": "en",
        })
    except Exception as exc:
        print(f"Reverse geocoding failed: {exc}")
        return None

    if data.get("error"):
        return None

    addr = data.get("address") or {}
    name = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or addr.get("hamlet")
        or data.get("name")
    )
    region = (
        addr.get("county")
        or addr.get("state_district")
        or addr.get("state")
        or ""
    )

    return {
        "name": name or f"{lat:.4f}, {lon:.4f}",
        "country": addr.get("country") or "",
        "country_code": (addr.get("country_code") or "").upper(),
        "region": region,
    }


def _days_from_hours(hours: int, max_days: int) -> int:
    days = max(1, int(hours / 24) + 1)
    return min(days, max_days)



# OPTIONAL PRECIPITATION PROBABILITY
def _request_weather_probability(endpoint: str, params: dict) -> dict:
    extra = dict(params)
    extra["hourly"] = params["hourly"] + ",precipitation_probability"
    try:
        return request(endpoint, extra)
    except ApiRequestError as exc:
        if exc.status is not None and 400 <= exc.status < 500 and exc.status != 429:
            return request(endpoint, params)
        raise


def fetch_weather(location, units: str, hours: int, model: str = "best_match") -> dict:
    """Fetch weather forecast. Matches main.py signature.

    HRES and IFS 0.25° use /v1/forecast with distinct model IDs.
    AIFS uses /v1/ecmwf. Other models use /v1/forecast.
    """
    if units == "imperial":
        t_unit, w_unit, p_unit = "fahrenheit", "mph", "inch"
    elif units == "ms":
        t_unit, w_unit, p_unit = "celsius", "ms", "mm"
    elif units == "knots":
        t_unit, w_unit, p_unit = "celsius", "kn", "mm"
    else:  # metric
        t_unit, w_unit, p_unit = "celsius", "kmh", "mm"

    days = _days_from_hours(hours, WEATHER_MAX_DAYS)
    is_ecmwf = model in ECMWF_MODELS

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "hourly": ECMWF_VARS if is_ecmwf else WEATHER_VARS,
        "daily": "sunrise,sunset",
        "forecast_days": days,
        "timezone": location.timezone,
        "temperature_unit": t_unit,
        "wind_speed_unit": w_unit,
        "precipitation_unit": p_unit,
    }
    if location.elevation is not None:
        params["elevation"] = location.elevation

    if model in ("ecmwf_ifs_hres", "ecmwf_ifs"):
        params["hourly"] = WEATHER_VARS
        params["models"] = (
            "ecmwf_ifs" if model == "ecmwf_ifs_hres"
            else "ecmwf_ifs025"
        )
        return _request_weather_probability(FORECAST, params)

    if is_ecmwf:
        model_value = ECMWF_MODEL_MAP.get(model)
        if model_value:
            params["models"] = model_value
        return _request_weather_probability(ECMWF, params)

    model_value = GENERIC_MODEL_MAP.get(model)
    if model_value:
        params["models"] = model_value
        try:
            return _request_weather_probability(FORECAST, params)
        except ApiRequestError as exc:
            if exc.status is not None and 400 <= exc.status < 500 and exc.status != 429:
                raise NoModelData(str(exc)) from exc
            raise
    return _request_weather_probability(FORECAST, params)

def fetch_gfs_uv(location, hours: int) -> dict:
    """Fetch only UV index from GFS Seamless for an optional fallback."""
    return request(FORECAST, {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "hourly": "uv_index",
        "forecast_days": _days_from_hours(hours, WEATHER_MAX_DAYS),
        "timezone": location.timezone,
        "models": "gfs_seamless",
    })

def fetch_air_quality(location, hours: int) -> dict:
    """Fetch air quality. Matches main.py signature.

    The air-quality API caps forecast_days at 7 and does not support the
    `models` parameter used by the weather forecast endpoint.
    """
    days = _days_from_hours(hours, AIR_MAX_DAYS)
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "hourly": AIR_VARS,
        "forecast_days": days,
        "timezone": location.timezone,
    }
    return request(AIR, params)
    
def fetch_marine(location, hours: int) -> dict:
    """Fetch optional marine series; do not mix them into weather data."""
    return request(MARINE, {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "hourly": (
            "sea_surface_temperature,sea_level_height_msl,"
            "wave_height,wave_period,wave_direction"
        ),
        "forecast_days": _days_from_hours(hours, WEATHER_MAX_DAYS),
        "timezone": location.timezone,
        "cell_selection": "sea",
    })
