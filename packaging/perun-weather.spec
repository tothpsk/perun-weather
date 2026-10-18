Name:           perun-weather
Version:        5.0.0
Release:        1%{?dist}
Summary:        Weather, made visible - interactive charts powered by Open-Meteo

License:        MIT
URL:            https://github.com/tothpsk/perun-weather
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  pyproject-rpm-macros
BuildRequires:  desktop-file-utils

Requires:       python3-gobject
Requires:       gtk4
Requires:       libadwaita
Requires:       webkitgtk6.0

%description
Perun Weather is a GTK4/libadwaita desktop application that visualises
forecasts, air quality, pollen, sun and moon data, optional marine data and
official weather alerts as interactive charts. Weather data by Open-Meteo.com,
licensed under CC BY 4.0.

%prep
%autosetup

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

install -Dpm 0644 data/io.github.tothpsk.PerunWeather.desktop \
  %{buildroot}%{_datadir}/applications/io.github.tothpsk.PerunWeather.desktop

install -Dpm 0644 data/io.github.tothpsk.PerunWeather.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/io.github.tothpsk.PerunWeather.svg
  
install -Dpm 0644 data/io.github.tothpsk.PerunWeather-symbolic.svg \
  %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps/io.github.tothpsk.PerunWeather-symbolic.svg

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.tothpsk.PerunWeather.desktop

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/perun_weather/
%{python3_sitelib}/perun_weather-*.dist-info/
%{_bindir}/perun-weather
%{_datadir}/applications/io.github.tothpsk.PerunWeather.desktop
%{_datadir}/icons/hicolor/scalable/apps/io.github.tothpsk.PerunWeather.svg
%{_datadir}/icons/hicolor/symbolic/apps/io.github.tothpsk.PerunWeather-symbolic.svg

%changelog
* Sun Oct 18 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 5.0.0-1
- Add the weather-at-a-glance overview and the 5-day outlook
- Add a settings panel grouped into Data, Panels and Charts
- Rename marine data to Marine panel
- Unify number formatting, degree signs and wind direction text
* Thu Oct 15 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 4.6.0-1
- Add precipitation probability strip and summary value
- Apply readable five-tick axes to forecast, air, pollen and marine charts
- Fit temperature and tide axes to visible data
- Fix daylight-saving day boundaries and unify chart spacing
* Tue Oct 13 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 4.5.1-1
- Fix precipitation baseline and align wind/pressure axes
- Add bilingual air indicator and styled AOD tooltips
- Keep normal air summary values neutral and match AQI formatting
- Update bilingual changelog, README and release metadata
* Mon Oct 12 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 4.5.0-1
- Add 13 weather models and Best match fallback
- Add persisted EU/US AQI selection and composite air/pollen indicator
- Add coloured weather summaries and separate precipitation types
- Fix marine chips, missing-data smoothing and wind direction arrows
- Update bilingual help, changelog and README
* Sun Oct 11 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 4.0.1-1
- Update the licensing notice in the help (copyright and MIT License)
- Credit Copernicus instead of CAMS for air quality data
- Disable page zoom (Ctrl + wheel, Ctrl + plus/minus/zero)
- Add Debian packaging
