Name: tendrl-node-agent
Version: 1.5.0
Release: 1%{?dist}
BuildArch: noarch
Summary: Module for Tendrl Node Agent
Source0: %{name}-%{version}.tar.gz
License: LGPLv2+
URL: https://github.com/Tendrl/node-agent

BuildRequires: python-urllib3
BuildRequires: python2-devel
BuildRequires: pytest
BuildRequires: systemd
BuildRequires: python-mock
BuildRequires: python-setuptools

Requires: collectd
Requires: collectd-ping
Requires: python-jinja2
Requires: tendrl-commons
Requires: hwinfo 
Requires: python-netifaces
Requires: python-netaddr
Requires: python-setuptools
Requires: rsyslog

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
install -m  0755  --directory $RPM_BUILD_ROOT%{_libdir}/collectd/gluster/low_weight
install -m  0755  --directory $RPM_BUILD_ROOT%{_libdir}/collectd/gluster/heavy_weight
install -m  0755  --directory $RPM_BUILD_ROOT%{_sysconfdir}/collectd_template
install -Dm 0644 tendrl-node-agent.service $RPM_BUILD_ROOT%{_unitdir}/tendrl-node-agent.service
install -Dm 0644 tendrl-node-agent.socket $RPM_BUILD_ROOT%{_unitdir}/tendrl-node-agent.socket
install -Dm 0644 etc/tendrl/node-agent/node-agent.conf.yaml.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent.conf.yaml
install -Dm 0644 etc/tendrl/node-agent/logging.yaml.syslog.sample $RPM_BUILD_ROOT%{_sysconfdir}/tendrl/node-agent/node-agent_logging.yaml
install -Dm 644 etc/tendrl/node-agent/*.sample $RPM_BUILD_ROOT%{_datadir}/tendrl/node-agent/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d
install -Dm 644 etc/rsyslog.d/tendrl-node-agent.conf $RPM_BUILD_ROOT/%{_sysconfdir}/rsyslog.d/tendrl-node-agent.conf
cp -a tendrl/node_agent/monitoring/collectd/collectors/* $RPM_BUILD_ROOT%{_libdir}/collectd/
cp -a tendrl/node_agent/monitoring/collectd/templates/ceph/* $RPM_BUILD_ROOT%{_sysconfdir}/collectd_template/
cp -a tendrl/node_agent/monitoring/collectd/templates/gluster/* $RPM_BUILD_ROOT%{_sysconfdir}/collectd_template/
cp -a tendrl/node_agent/monitoring/collectd/templates/node/* $RPM_BUILD_ROOT%{_sysconfdir}/collectd_template/

%post
getent group tendrl >/dev/null || groupadd -r tendrl
getent passwd tendrl-user >/dev/null || \
    useradd -r -g tendrl -d /var/lib/tendrl -s /sbin/nologin \
    -c "Tendrl node user" tendrl-user
systemctl enable tendrl-node-agent

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
%attr(0655, root, root) %{_sysconfdir}/collectd_template/*
%attr(0655, root, root) %{_libdir}/collectd/*

%doc README.rst
%license LICENSE
%{_datadir}/tendrl/node-agent/
%config(noreplace) %{_sysconfdir}/tendrl/node-agent/*.yaml
%{_unitdir}/tendrl-node-agent.service
%{_unitdir}/tendrl-node-agent.socket
%config(noreplace) %{_sysconfdir}/rsyslog.d/tendrl-node-agent.conf

%changelog
* Fri Aug 04 2017 Rohan Kanade <rkanade@redhat.com> - 1.5.0-1
- Release tendrl-node-agent v1.5.0

* Mon Jun 19 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.2-1
- Release tendrl-node-agent v1.4.2

* Sun Jun 11 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.1-2
- Fixes https://github.com/Tendrl/commons/issues/586

* Thu Jun 08 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.1-1
- Release tendrl-node-agent v1.4.1

* Fri Jun 02 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.0-2
- Fixes https://github.com/Tendrl/node-agent/issues/481

* Fri Jun 02 2017 Rohan Kanade <rkanade@redhat.com> - 1.4.0-1
- Release tendrl-node-agent v1.4.0

* Thu May 18 2017 Rohan Kanade <rkanade@redhat.com> - 1.3.0-1
- Release tendrl-node-agent v1.3.0

* Tue Apr 18 2017 Rohan Kanade <rkanade@redhat.com> - 1.2.3-1
- Release tendrl-node-agent v1.2.3

* Sat Apr 01 2017 Rohan Kanade <rkanade@redhat.com> - 1.2.2-1
- Release tendrl-node-agent v1.2.2

* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
