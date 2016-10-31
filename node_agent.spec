%define pkg_name tendrl-node-agent
%define pkg_version 0.0.1
%define pkg_release 1

Name: %{pkg_name}
Version: %{pkg_version}
Release: %{pkg_release}%{?dist}
BuildArch: noarch
Summary: Common Module for All Bridges
Source0: %{pkg_name}-%{pkg_version}.tar.gz
Group:   Applications/System
License: LGPL2.1
Url: https://github.com/Tendrl/node_agent

Requires: python-etcd >= 0.4.3
Requires: python-gevent >= 1.0.2
Requires: python-greenlet >= 0.3.2
Requires: python-taskflow >= 2.6
Requires: collectd >= 5.5.1
Requires: python-jinja2 >= 2.7.2
Requires: tendrl-bridge-common

%description
Python module for Tendrl node bridge to manage storage node in the sds cluster

%prep
%setup -n %{pkg_name}-%{pkg_version}
# Remove the requirements file to avoid adding into
# distutils requiers_dist config
rm -rf {test-,}requirements.txt

# Remove bundled egg-info
rm -rf %{pkg_name}.egg-info

%build
%{__python} setup.py build

# generate html docs
%if 0%{?rhel}==7
sphinx-1.0-build doc/source html
%else
sphinx-build doc/source html
%endif
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%{__python} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -Dm 0644 tendrl-noded.service $RPM_BUILD_ROOT/usr/lib/systemd/system/tendrl-noded.service

%post
%systemd_post tendrl-noded.service

%preun
%systemd_preun tendrl-noded.service

%postun
%systemd_postun_with_restart tendrl-noded.service

%files -f INSTALLED_FILES
%doc html README.rst
%license LICENSE
%{_usr}/lib/systemd/system/tendrl-noded.service

%changelog
* Tue Nov 01 2016 Timothy Asir Jeyasingh <tjeyasin@redhat.com> - 0.0.1-1
- Initial build.
