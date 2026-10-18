from __future__ import annotations
import json
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_DIR = "perun-weather"
CONFIG = Path.home() / ".config" / APP_DIR
CACHE = Path.home() / ".cache" / APP_DIR

_LEGACY_CONFIG = Path.home() / ".config" / "meteogram"


def _migrate_legacy_config() -> None:
    """One-time move of settings from the former 'meteogram' directory."""
    old_file = _LEGACY_CONFIG / "settings.json"
    new_file = CONFIG / "settings.json"
    if old_file.exists() and not new_file.exists():
        try:
            CONFIG.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_file, new_file)
        except OSError:
            pass

@dataclass
class Location:
    name: str
    country: str
    latitude: float
    longitude: float
    elevation: float | None = None
    timezone: str = "auto"
    country_code: str = ""
    region: str = ""
    admin: str = ""

@dataclass
class Settings:
    locations: list[Location] = field(default_factory=lambda: [
        Location(
            name="Prešov",
            country="Slovakia",
            latitude=48.9987,
            longitude=21.2339,
            elevation=250.0,
            timezone="Europe/Bratislava",
            country_code="SK",
            region="Prešov Region",
        )
    ])
    selected: int = 0
    model: str = "best_match"
    interval: int = 3
    days: int = 5
    hours: int = 72
    units: str = "metric"
    smoothing: int = 0
    auto: bool = True
    lang: str = "sk"
    marine_enabled: bool = False
    aqi_scale: str = "eu"
    radar_enabled: bool = False
    radar_client_id: str = ""
    radar_client_secret: str = ""

def load() -> Settings:
    _migrate_legacy_config()
    CONFIG.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        raw = json.loads((CONFIG / "settings.json").read_text(encoding="utf-8"))
        raw["locations"] = [Location(**x) for x in raw["locations"]]
        out = Settings(**raw)
        out.selected = max(0, min(out.selected, len(out.locations) - 1))
        return out
    except Exception:
        return Settings()

def save(settings: Settings) -> None:
    CONFIG.mkdir(parents=True, exist_ok=True)
    (CONFIG / "settings.json").write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        (CONFIG / "settings.json").chmod(0o600)
    except OSError:
        pass

def cache_file(location: Location) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / f"forecast_{location.latitude:.4f}_{location.longitude:.4f}.json"

def load_cache(location: Location) -> dict | None:
    try:
        return json.loads(cache_file(location).read_text(encoding="utf-8"))
    except Exception:
        return None

def save_cache(location: Location, data: dict) -> None:
    cache_file(location).write_text(json.dumps(data), encoding="utf-8")
