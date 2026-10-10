"""
Thin entry-point script used only by PyInstaller.

PyInstaller's Analysis needs a concrete .py file to start tracing imports
from -- it can't be pointed at "python -m perun_weather.main_windows" directly.
This file just imports and calls the real app.

Keep this file in the SAME folder as the "perun_weather" package folder and
as perun_weather_qt_windows.spec, e.g.:

    perun-weather\\
        perun_weather\\                 <- the package (main_windows.py, api.py, ...)
        perun_weather_entry.py          <- this file
        perun_weather_qt_windows.spec
"""
from perun_weather.main_windows import main

if __name__ == "__main__":
    main()
