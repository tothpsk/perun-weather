Name:           perun-weather
Version:        4.0.1
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
* Sun Oct 11 2026 Peter Tóth <tothpsk@users.noreply.github.com> - 4.0.1-1
- Update the licensing notice in the help (copyright and MIT License)
- Credit Copernicus instead of CAMS for air quality data
- Disable page zoom (Ctrl + wheel, Ctrl + plus/minus/zero)
- Add Debian packaging
