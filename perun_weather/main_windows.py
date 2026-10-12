from __future__ import annotations

import json
import re
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QColor
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow

from . import alerts
from . import api
from .config import Location, load, load_cache, save, save_cache
from .normalize import prepare


ASSETS = Path(__file__).parent / "data"
EUROPE_BOUNDS = {
    "min_lat": 34.0,
    "max_lat": 72.5,
    "min_lon": -25.5,
    "max_lon": 45.5,
}
EUROPE_ONLY_MODELS = {"icon_d2", "icon_eu", "arpege_europe", "knmi_arome_europe", "chmi_aladin_ce_2km", "chmi_aladin_cz_1km"}

COORD_PATTERN = re.compile(
    r"^\s*"
    r"(-?\d+(?:\.\d+)?)\s*°?\s*([NSEW])?\.?\s*"
    r"[,;\s]+\s*"
    r"(-?\d+(?:\.\d+)?)\s*°?\s*([NSEW])?\.?\s*$",
    re.IGNORECASE,
)


def _parse_coordinates(query: str):
    """Return (latitude, longitude) for a decimal coordinate pair, or None."""
    m = COORD_PATTERN.match(query.strip())
    if not m:
        return None

    a_val, a_hem, b_val, b_hem = m.groups()
    a_val, b_val = float(a_val), float(b_val)
    a_hem = (a_hem or "").upper()
    b_hem = (b_hem or "").upper()

    if a_hem in ("N", "S") or b_hem in ("E", "W"):
        lat, lat_hem, lon, lon_hem = a_val, a_hem, b_val, b_hem
    elif a_hem in ("E", "W") or b_hem in ("N", "S"):
        lon, lon_hem, lat, lat_hem = a_val, a_hem, b_val, b_hem
    else:
        lat, lat_hem, lon, lon_hem = a_val, "", b_val, ""

    if lat_hem == "S":
        lat = -abs(lat)
    elif lat_hem == "N":
        lat = abs(lat)
    if lon_hem == "W":
        lon = -abs(lon)
    elif lon_hem == "E":
        lon = abs(lon)

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return round(lat, 4), round(lon, 4)


class Bridge(QObject):
    """Methods available to chart.html through Qt QWebChannel."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    @Slot()
    def refresh(self):
        print("[BRIDGE] refresh received")
        self.app.handle_action({"action": "refresh"})

    @Slot(int)
    def select(self, index):
        self.app.handle_action({"action": "select", "index": index})

    @Slot(int)
    def delete(self, index):
        self.app.handle_action({"action": "delete", "index": index})

    @Slot(str)
    def reorder(self, order_json):
        self.app.handle_action({"action": "reorder", "order": order_json})

    @Slot(str)
    def add(self, query):
        print(f"[BRIDGE] add received: {query!r}")
        self.app.handle_action({"action": "add", "query": query})

    @Slot(str)
    def add_confirm(self, location_json):
        print(f"[BRIDGE] add_confirm received: {location_json!r}")
        self.app.handle_action(
            {"action": "add_confirm", "location": location_json}
        )

    @Slot(str, str)
    def setting(self, key, value):
        self.app.handle_action(
            {"action": "setting", "key": key, "value": value}
        )


class App(QObject):
    """Windows desktop application shell implemented with Qt WebEngine."""

    search_results_ready = Signal(str)
    refresh_finished = Signal(object, object, int)
    model_fallback = Signal(str, str, int)

    def __init__(self):
        super().__init__()

        self.settings = load()

        self.qt_app = QApplication.instance() or QApplication([])
        self.window = QMainWindow()
        self.window.setWindowTitle("Perun Weather")
        self.window.resize(1800, 940)

        self.web = QWebEngineView()
        self.web.page().setBackgroundColor(QColor("#1e2129"))
        self.window.setCentralWidget(self.web)

        self.bridge = Bridge(self)
        self.channel = QWebChannel(self.web.page())
        self.channel.registerObject("bridge", self.bridge)
        self.web.page().setWebChannel(self.channel)

        self.ready = False
        self.timer = QTimer(self.window)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.refresh)

        self.refresh_generation = 0
        self.refresh_pending = False

        self.web.loadFinished.connect(self.on_loaded)
        self.search_results_ready.connect(self._render_search_results)
        self.refresh_finished.connect(self._finish_refresh)
        self.model_fallback.connect(self._fallback_to_best_match)

    def start(self):
        self.window.show()
        self.web.load(QUrl.fromLocalFile(str(ASSETS / "chart.html")))
        return self.qt_app.exec()

    def on_loaded(self, ok):
        if not ok:
            print("Unable to load chart.html")
            return

        self.ready = True
        self.push_locations()
        self.refresh()

    def call_js(self, script):
        if self.ready:
            self.web.page().runJavaScript(script)

    def is_european_location(self, location):
        return (
            EUROPE_BOUNDS["min_lat"] <= location.latitude <= EUROPE_BOUNDS["max_lat"]
            and EUROPE_BOUNDS["min_lon"] <= location.longitude <= EUROPE_BOUNDS["max_lon"]
        )

    def ensure_model_available(self):
        if not self.settings.locations:
            return False

        location = self.settings.locations[self.settings.selected]

        if (
            self.settings.model in EUROPE_ONLY_MODELS
            and not self.is_european_location(location)
        ):
            unavailable = self.settings.model
            self.settings.model = "best_match"
            save(self.settings)

            message = api.msg(
                self.settings.lang,
                "europe_only",
                model=api.MODEL_LABELS.get(unavailable, unavailable),
            )
            self.call_js("showToast(" + json.dumps(message) + ")")
            return True

        return False

    def handle_action(self, message):
        try:
            action = message.get("action")
            refresh_needed = False

            if action == "refresh":
                refresh_needed = True

            elif action == "select":
                self.settings.selected = int(message["index"])
                self.settings.selected = max(
                    0,
                    min(
                        self.settings.selected,
                        len(self.settings.locations) - 1,
                    ),
                )
                self.ensure_model_available()
                save(self.settings)
                self.push_locations()
                self.redraw_from_cache()
                refresh_needed = True

            elif action == "delete":
                index = int(message["index"])

                if (
                    len(self.settings.locations) > 1
                    and 0 <= index < len(self.settings.locations)
                ):
                    self.settings.locations.pop(index)
                    self.settings.selected = min(
                        self.settings.selected,
                        len(self.settings.locations) - 1,
                    )
                    self.ensure_model_available()
                    save(self.settings)
                    self.push_locations()
                    self.redraw_from_cache()
                    refresh_needed = True

            elif action == "reorder":
                order = [
                    int(item)
                    for item in json.loads(message.get("order", "[]"))
                ]
                old = self.settings.locations[:]

                if sorted(order) == list(range(len(old))):
                    selected_location = old[self.settings.selected]
                    self.settings.locations = [old[index] for index in order]
                    self.settings.selected = self.settings.locations.index(
                        selected_location
                    )
                    save(self.settings)
                    self.push_locations()

            elif action == "add":
                query = message.get("query", "").strip()

                if query:
                    threading.Thread(
                        target=self._search_worker,
                        args=(query,),
                        daemon=True,
                    ).start()

            elif action == "add_confirm":
                item = json.loads(message.get("location", "{}"))

                location = Location(
                    name=item["name"],
                    country=item.get("country", ""),
                    latitude=float(item["latitude"]),
                    longitude=float(item["longitude"]),
                    country_code=item.get("country_code", ""),
                    region=item.get("region", ""),
                )

                duplicate = any(
                    abs(existing.latitude - location.latitude) < 0.001
                    and abs(existing.longitude - location.longitude) < 0.001
                    for existing in self.settings.locations
                )

                if not duplicate:
                    self.settings.locations.append(location)
                    self.settings.selected = len(self.settings.locations) - 1
                    self.ensure_model_available()
                    save(self.settings)
                    self.push_locations()
                    self.redraw_from_cache()
                    refresh_needed = True

            elif action == "setting":
                key = message.get("key")
                value = message.get("value")

                if key == "auto":
                    self.settings.auto = value == "true"

                elif key == "units":
                    self.settings.units = value
                    refresh_needed = True

                elif key == "hours":
                    self.settings.hours = int(value)
                    refresh_needed = True

                elif key == "model":
                    self.settings.model = value
                    self.ensure_model_available()
                    refresh_needed = True

                elif key == "interval":
                    self.settings.interval = int(value)
                    self.redraw_from_cache()

                elif key == "smoothing":
                    self.settings.smoothing = int(value)
                    self.redraw_from_cache()

                elif key == "lang":
                    self.settings.lang = value

                elif key == "marine_enabled":
                    self.settings.marine_enabled = value == "true"
                    refresh_needed = True

                save(self.settings)
                self.push_locations()

                if key == "auto":
                    self._arm_timer()

            if refresh_needed:
                self.refresh()

        except Exception as exc:
            print(f"Error handling action {message}: {exc}")

    def _search_worker(self, query):
        try:
            coords = _parse_coordinates(query)
            if coords is not None:
                lat, lon = coords
                place = api.reverse_geocode(lat, lon) or {}

                results = [{
                    "name": place.get("name") or f"{lat:.4f}, {lon:.4f}",
                    "country": place.get("country", ""),
                    "country_code": place.get("country_code", ""),
                    "region": place.get("region", ""),
                    "latitude": lat,
                    "longitude": lon,
                }]
            else:
                results = api.geocode(query)
        except Exception as exc:
            print(f"Search failed: {exc}")
            results = []

        self.search_results_ready.emit(json.dumps(results, ensure_ascii=False))

    def _render_search_results(self, results_json):
        self.call_js("renderSearchResults(" + results_json + ")")

    def push_locations(self):
        selected_location = (
            self.settings.locations[self.settings.selected]
            if self.settings.locations
            else None
        )

        icon_available = bool(
            selected_location
            and self.is_european_location(selected_location)
        )

        payload = {
            "locations": [
                {
                    "name": location.name,
                    "country": location.country,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
                for location in self.settings.locations
            ],
            "selected": self.settings.selected,
            "units": self.settings.units,
            "hours": self.settings.hours,
            "auto": self.settings.auto,
            "model": self.settings.model,
            "interval": self.settings.interval,
            "smoothing": self.settings.smoothing,
            "icon_models_available": icon_available,
            "lang": self.settings.lang,
            "marine_enabled": self.settings.marine_enabled,
        }

        self.call_js(
            "setAppState(" + json.dumps(payload, ensure_ascii=False) + ")"
        )

    def refresh(self):
        if not self.settings.locations:
            return

        self.refresh_generation += 1
        generation = self.refresh_generation

        location = self.settings.locations[self.settings.selected]
        units = self.settings.units
        hours = self.settings.hours
        model = self.settings.model
        marine_enabled = self.settings.marine_enabled
        self.refresh_pending = True
        self.call_js("setRefreshing(true)")

        threading.Thread(
            target=self._refresh_worker,
            args=(location, units, hours, model, marine_enabled, generation),
            daemon=True,
        ).start()

    def redraw_from_cache(self):
        if not self.settings.locations:
            return

        location = self.settings.locations[self.settings.selected]
        cached = load_cache(location)

        if cached:
            self.call_js(
                "renderForecast("
                + json.dumps(cached, ensure_ascii=False)
                + ")"
            )

    def _refresh_worker(self, location, units, hours, model, marine_enabled, generation):
        try:
            weather = api.fetch_weather(location, units, hours, model)

            hourly = weather.get("hourly", {})
            temperatures = hourly.get("temperature_2m") or []

            if not any(value is not None for value in temperatures):
                raise api.NoModelData(
                    f"{model.replace('_', ' ').upper()} returned no hourly "
                    f"temperature data for {location.name}. "
                    "Choose another weather model."
                )

            times = hourly.get("time") or []
            original_uv = hourly.get("uv_index") or []
            uv_sources = [
                "selected" if i < len(original_uv) and original_uv[i] is not None else None
                for i in range(len(times))
            ]

            if model != "gfs" and any(source is None for source in uv_sources):
                try:
                    uv_sources = merge_uv_fallback(
                        weather, api.fetch_gfs_uv(location, hours)
                    )
                except Exception as exc:
                    print(f"Optional GFS UV fallback unavailable: {exc}")

            weather["uv_sources"] = uv_sources
            
            marine = None
            marine_error = None

            if marine_enabled:
                try:
                    marine = api.fetch_marine(location, hours)
                except Exception as exc:
                    marine_error = str(exc)
                    print(f"Optional marine forecast unavailable: {exc}")

            air = api.fetch_air_quality(location, hours)
            if (location.country_code or "").upper() in alerts.METEOALARM_CC:
                official_alerts = alerts.fetch_official_alerts(
                    location.country_code, location.region
                )
            else:
                official_alerts = alerts.fetch_kde_alerts(
                    location.latitude, location.longitude
                )

            payload = prepare(
                location,
                weather,
                air,
                units,
                official_alerts=official_alerts,
            )
            payload["marine"] = marine
            payload["marine_error"] = marine_error

            save_cache(location, payload)
            self.refresh_finished.emit(payload, None, generation)

        except api.NoModelData:
            if model != "best_match":
                self.model_fallback.emit(model, location.name, generation)
            else:
                cached = load_cache(location)
                self.refresh_finished.emit(
                    cached,
                    api.msg(self.settings.lang, "no_data_final", place=location.name),
                    generation,
                )
        except api.ApiRequestError as exc:
            print(f"Weather request failed: {exc}")
            cached = load_cache(location)
            self.refresh_finished.emit(
                cached,
                api.msg(self.settings.lang, "request_failed"),
                generation,
            )
        except Exception as exc:
            cached = load_cache(location)
            self.refresh_finished.emit(cached, str(exc), generation)

    def _fallback_to_best_match(self, unavailable, place, generation):
        if generation != self.refresh_generation:
            return
        if self.settings.model == unavailable:
            self.settings.model = "best_match"
            save(self.settings)
            self.push_locations()
            message = api.msg(
                self.settings.lang,
                "no_data",
                model=api.MODEL_LABELS.get(unavailable, unavailable),
                place=place,
            )
            self.call_js("showToast(" + json.dumps(message, ensure_ascii=False) + ")")
            self.refresh()

    def _finish_refresh(self, payload, error, generation):
        if generation != self.refresh_generation:
            return

        self.refresh_pending = False
        self.call_js("setRefreshing(false)")

        if payload:
            self.call_js(
                "renderForecast("
                + json.dumps(payload, ensure_ascii=False)
                + ")"
            )

            if error:
                self.call_js("showToast(" + json.dumps(error) + ")")
        else:
            self.call_js("showToast('Unable to load forecast data.')")

        now = datetime.now().strftime("%H:%M")

        if self.settings.auto:
            next_time = datetime.fromtimestamp(
                datetime.now().timestamp() + 21600
            ).strftime("%H:%M")
            status = (
                f"Last updated: {now} · next auto-refresh: {next_time}"
            )
        else:
            status = f"Last updated: {now} · auto-refresh disabled"

        self.call_js(
            "setStatus(" + json.dumps(status, ensure_ascii=False) + ")"
        )
        self._arm_timer()

    def _arm_timer(self):
        self.timer.stop()

        if self.settings.auto:
            self.timer.start(21600 * 1000)


def main():
    return App().start()

def merge_uv_fallback(weather: dict, gfs_uv: dict) -> list[str | None]:
    """Fill missing UV by local timestamp and return a source per hour."""
    primary = weather.get("hourly") or {}
    times = primary.get("time") or []
    original = primary.get("uv_index") or []

    secondary = gfs_uv.get("hourly") or {}
    gfs_by_time = dict(zip(
        secondary.get("time") or [],
        secondary.get("uv_index") or [],
    ))

    merged = []
    sources = []
    for i, timestamp in enumerate(times):
        selected_value = original[i] if i < len(original) else None
        fallback_value = gfs_by_time.get(timestamp)

        if selected_value is not None:
            merged.append(selected_value)
            sources.append("selected")
        elif fallback_value is not None:
            merged.append(fallback_value)
            sources.append("gfs")
        else:
            merged.append(None)
            sources.append(None)

    primary["uv_index"] = merged
    weather["hourly"] = primary
    return sources


if __name__ == "__main__":
    raise SystemExit(main())
