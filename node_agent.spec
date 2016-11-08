Name: tendrl-node-agent
Version: 0.0.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Node Agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/node_agent

BuildRequires: systemd
BuildRequires: python2-devel
BuildRequires: python-sphinx
BuildRequires: pytest

Requires: python-etcd
Requires: python-gevent
Requires: python-greenlet
Requires: python-taskflow
Requires: collectd
Requires: python-jinja2
Requires: tendrl-bridge-common
Requires: systemd

%description
Python module for Tendrl node bridge to manage storage node in the sds cluster

%prep
%setup %{name}-%{version}
# Remove the requirements file to avoid adding into
# distutils requiers_dist config
rm -rf {test-,}requirements.txt

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 0644 tendrl-noded.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-noded.service

%post
%systemd_post tendrl-noded.service

%preun
%systemd_preun tendrl-noded.service

%postun
%systemd_postun_with_restart tendrl-noded.service

%check
py.test -v tendrl/node_agent/tests

%files -f INSTALLED_FILES
%doc README.rst
%license LICENSE
%{_unitdir}/tendrl-noded.service

%changelog
* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
