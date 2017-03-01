Name: tendrl-node-agent
Version: 1.2.1
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Node Agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/node-agent

BuildRequires: ansible
BuildRequires: python-gevent
BuildRequires: python-etcd
BuildRequires: python-urllib3
BuildRequires: python2-devel
BuildRequires: pytest
BuildRequires: systemd
BuildRequires: python-mock

Requires: ansible
Requires: python-etcd
Requires: python-gevent
Requires: python-greenlet
Requires: collectd
Requires: python-jinja2
Requires: tendrl-commons
Requires: hwinfo 

%description
Python module for Tendrl node bridge to manage storage node in the sds cluster

%prep
%setup

# Remove bundled egg-info
rm -rf %{name}.egg-info

%build
%{__python} setup.py build

# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -m  0755  --directory $RPM_BUILD_ROOT%{_var}/log/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_datadir}/tendrl/node-agent
install -m  0755  --directory $RPM_BUILD_ROOT%{_sharedstatedir}/tendrl
install -Dm 0644 tendrl-node-agent.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-node-agent.service
install -Dm 0644 tendrl-node-agent.socket $RPM_BUILD_ROOT%{_unitdir}/tendrl-node-agent.socket
install -Dm 0644 etc/tendrl/node-agent/node-agent.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent.conf.yaml
install -Dm 0644 etc/tendrl/node-agent/logging.yaml.syslog.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent_logging.yaml
install -Dm 644 etc/tendrl/node-agent/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/node-agent/

%post
getent group tendrl >/dev/null || groupadd -r tendrl
%systemd_post tendrl-node-agent.service

%preun
%systemd_preun tendrl-node-agent.service

%postun
%systemd_postun_with_restart tendrl-node-agent.service

%check
py.test -v tendrl/node-agent/tests || :

%files -f INSTALLED_FILES
%dir %{_var}/log/tendrl/node-agent
%dir %{_sysconfdir}/tendrl/node-agent
%dir %{_datadir}/tendrl/node-agent
%dir %{_sharedstatedir}/tendrl
%doc README.rst
%license LICENSE
%{_datadir}/tendrl/node-agent/
%{_sysconfdir}/tendrl/node-agent/node-agent.conf.yaml
%{_sysconfdir}/tendrl/node-agent/node-agent_logging.yaml
%{_unitdir}/tendrl-node-agent.service
%{_unitdir}/tendrl-node-agent.socket

%changelog
* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
