#
# lxc: linux Container library
#
# (C) Copyright IBM Corp. 2007, 2008
#
# Authors:
# Daniel Lezcano <daniel.lezcano at free.fr>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

# Set with_systemd on distros that use it, so we can install the service
# file, otherwise the sysvinit script will be installed
%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1210
%global with_systemd 1
%define init_script systemd
#
# BuildRequires systemd-units on fedora and rhel
%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
BuildRequires: systemd-units
%endif
#
# BuildRequires systemd on openSUSE and SUSE
%if 0%{?suse_version} >= 1210
BuildRequires: systemd
%endif
%else
%global with_systemd 0
%define init_script sysvinit
%endif

# Must use /var/run for runtime_path on older releases or dnsmasq in the
# lxc-net script will not be able to write its pid in /run (selinux denial)
%if 0%{?fedora} < 15 || 0%{?rhel} < 7
%define _with_runtime_path --with-runtime-path=/var/run
%endif

# RPM needs alpha/beta/rc in Release: not Version: to ensure smooth
# package upgrades from alpha->beta->rc->release. For more info see:
# http://fedoraproject.org/wiki/Packaging%3aNamingGuidelines#NonNumericRelease
%if "x" != "x"
%global beta_rel 
%global beta_dot .%{beta_rel}
%else
%global norm_rel 1
%endif

Name: lxc
Version: 3.1.0
Release: %{?beta_rel:0.1.%{beta_rel}}%{?!beta_rel:%{norm_rel}}%{?dist}
URL: http://linuxcontainers.org
Source: http://linuxcontainers.org/downloads/%{name}-%{version}%{?beta_dot}.tar.gz
Summary: Linux Containers userspace tools
Group: Applications/System
License: LGPLv2+
BuildRoot: %{_tmppath}/%{name}-%{version}-build
Requires: openssl rsync dnsmasq bridge-utils
Requires: %{name}-libs = %{version}-%{release}
Requires(pre): /usr/sbin/useradd
Requires(postun): /usr/sbin/userdel
%if 0%{?fedora} < 15 || 0%{?rhel} < 7
Requires: libcgroup
%endif
# Note for Suse.  The "docbook2X" BuildRequires does properly
# match docbook2x on Suse in a case insensitive manner
BuildRequires: libcap libcap-devel docbook2X graphviz libxslt pkgconfig

#
# Additional packages for openSUSE and SUSE
#
%if 0%{?suse_version} >= 1210
PreReq:   permissions
BuildRequires:  libapparmor-devel linux-glibc-devel lsb-release docbook-utils

#
# libseccomp-devel only needed on i386/i586/i686 and X86_64
#
%ifarch %ix86 x86_64
BuildRequires:  libseccomp-devel
%endif
%endif

#
# Additional package for Tizen
#
%if %{defined tizen_version}
BuildRequires:  pkgconfig(dlog)
%endif

%description
Containers are insulated areas inside a system, which have their own namespace
for filesystem, network, PID, IPC, CPU and memory allocation and which can be
created using the Control Group and Namespace features included in the Linux
kernel.

This package provides the lxc-* tools, which can be used to start a single
daemon in a container, or to boot an entire "containerized" system, and to
manage and debug your containers.

%package	libs
Summary:	Shared library files for %{name}
Group:		System Environment/Libraries
%description	libs
The %{name}-libs package contains libraries for running %{name} applications.

%package	devel
Summary:	Development library for %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}, pkgconfig
%description	devel
The %{name}-devel package contains header files and library needed for
development of the Linux containers.

%prep
%setup -q -n %{name}-%{version}%{?beta_dot}
%build
PATH=$PATH:/usr/sbin:/sbin %configure $args \
%if "x%{_unitdir}" != "x"
  --with-systemdsystemunitdir=%{_unitdir} \
%endif
  %{?_with_runtime_path} \
  --disable-rpath \
  --with-init-script=%{init_script}
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
find %{buildroot} -type f -name '*.la' -exec rm -f {} ';'

%clean
rm -rf %{buildroot}

%pre
# Ensure that lxc-dnsmasq uid & gid gets correctly allocated
if getent passwd lxc-dnsmasq >/dev/null 2>&1 ; then : ; else \
 /usr/sbin/useradd -M -r -s /sbin/nologin \
 -c "LXC Networking Service" -d %_localstatedir/%name lxc-dnsmasq 2> /dev/null \
 || exit 1
fi

%post
# This test should trigger a network configure on a new install.
if [ ! -d /usr/local/etc/default ]
then
	mkdir -p /usr/local/etc/default
fi

if [ ! -f /usr/local/etc/default/lxc-net ] || ! grep -q 'USE_LXC_BRIDGE=' /usr/local/etc/default/lxc-net
then
	# Grab a random 10net subnet.  Need to add test logic...
	while [ true ]
	do
		SUBNET=10.$(($RANDOM % 256)).$(($RANDOM % 256))
		if ! ip -4 route ls | grep -q "^$SUBNET"
		then
			break
		fi
	done

	cat >  /usr/local/etc/default/lxc-net <<EOF
# Leave USE_LXC_BRIDGE as "true" if you want to use lxcbr0 for your
# containers.  Set to "false" if you'll use virbr0 or another existing
# bridge, or macvlan to your host's NIC.
USE_LXC_BRIDGE="true"

# If you change the LXC_BRIDGE to something other than lxcbr0, then
# you will also need to update your /etc/lxc/default.conf as well as the
# configuration (/var/lib/lxc/<container>/config) for any containers
# already created using the default config to reflect the new bridge
# name.
# If you have the dnsmasq daemon installed, you'll also have to update
# /etc/dnsmasq.d/lxc and restart the system wide dnsmasq daemon.
LXC_BRIDGE="lxcbr0"
LXC_BRIDGE_MAC="00:16:3e:00:00:00"
LXC_ADDR="$SUBNET.1"
LXC_NETMASK="255.255.255.0"
LXC_NETWORK="$SUBNET.0/24"
LXC_DHCP_RANGE="$SUBNET.2,$SUBNET.254"
LXC_DHCP_MAX="253"
# Uncomment the next line if you'd like to use a conf-file for the lxcbr0
# dnsmasq.  For instance, you can use 'dhcp-host=mail1,10.0.3.100' to have
# container 'mail1' always get ip address 10.0.3.100.
#LXC_DHCP_CONFILE=/etc/lxc/dnsmasq.conf

# Uncomment the next line if you want lxcbr0's dnsmasq to resolve the .lxc
# domain.  You can then add "server=/lxc/10.0.3.1' (or your actual $LXC_ADDR)
# to /etc/dnsmasq.conf, after which 'container1.lxc' will resolve on your
# host.
#LXC_DOMAIN="lxc"
EOF
fi

%postun
/usr/sbin/userdel lxc-dnsmasq > /dev/null 2>&1 || :

%post   libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_bindir}/*
# openSUSE/SUSE
%if 0%{?suse_version} >= 1210
%dir  %{_sysconfdir}/apparmor.d
%dir  %{_sysconfdir}/apparmor.d/abstractions
%dir  %{_sysconfdir}/apparmor.d/abstractions/%{name}
%config %{_sysconfdir}/apparmor.d/abstractions/%{name}/container-base
%config %{_sysconfdir}/apparmor.d/abstractions/%{name}/start-container
%config %{_sysconfdir}/apparmor.d/%{name}-containers
%dir  %{_sysconfdir}/apparmor.d/%{name}
%config %{_sysconfdir}/apparmor.d/%{name}/%{name}-default
%config %{_sysconfdir}/apparmor.d/%{name}/%{name}-default-with-mounting
%config %{_sysconfdir}/apparmor.d/%{name}/%{name}-default-with-nesting
%config %{_sysconfdir}/apparmor.d/usr.bin.%{name}-start
%endif
%{_mandir}/man1/lxc*
%{_mandir}/man5/lxc*
%{_mandir}/man7/lxc*
# not openSUSE/SUSE
%if %{undefined suse_version}
%{_mandir}/ja/man1/lxc*
%{_mandir}/ja/man5/lxc*
%{_mandir}/ja/man7/lxc*
%{_mandir}/ko/man1/lxc*
%{_mandir}/ko/man5/lxc*
%{_mandir}/ko/man7/lxc*
%endif
%{_datadir}/doc/*
%{_datadir}/lxc/*
%{_sysconfdir}/bash_completion.d
%config(noreplace) %{_sysconfdir}/lxc/*
%config(noreplace) %{_sysconfdir}/sysconfig/*

%if %{with_systemd}
%{_unitdir}/lxc-net.service
%{_unitdir}/lxc.service
%{_unitdir}/lxc@.service
%else
%{_sysconfdir}/rc.d/init.d/lxc
%{_sysconfdir}/rc.d/init.d/lxc-net
%endif

%files libs
%defattr(-,root,root)
%{_sbindir}/*
%{_libdir}/*.so.*
%{_libdir}/*.a
%{_libdir}/%{name}
%{_localstatedir}/*
%{_libexecdir}/%{name}/hooks/unmount-namespace
%{_libexecdir}/%{name}/lxc-apparmor-load
%{_libexecdir}/%{name}/lxc-monitord
%attr(4111,root,root) %{_libexecdir}/%{name}/lxc-user-nic
%if %{with_systemd}
%attr(555,root,root) %{_libexecdir}/%{name}/lxc-net
%attr(555,root,root) %{_libexecdir}/%{name}/lxc-containers
%endif

%files devel
%defattr(-,root,root)
%{_includedir}/%{name}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%changelog
* Tue Oct 22 2013 Dwight Engen <dwight.engen@oracle.com> - 1.0.0-0.1.alpha2
- fix some rpmlint warnings/errors
- split lua bits into separate package

* Mon Sep 10 2012 Dwight Engen <dwight.engen@oracle.com> - 0.8.0
- fix lxc-init moved to libexec
- .pc moved to _libdir
- package template files /usr/share/lxc/templates

* Thu Sep  8 2011 Greg Kurz <gkurz@fr.ibm.com> - 0.7.5.1
- fix installed files for rpmbuild
- introduce lxc-libs package

* Fri Jul 23 2010 Daniel Lezcano <dlezcano@fr.ibm.com> - 0.7.2
- set attribute for installed files
- fix libraries installation

* Tue Mar 24 2009 Daniel Lezcano <daniel.lezcano@free.fr> - 0.6.1
- Removed capability setting, let the user to do that through "lxc-setcap"

* Mon Feb 16 2009 Daniel Lezcano <daniel.lezcano@free.fr> - 0.6.0
- Added more capabilities to the executables

* Sun Jan 25 2009 Daniel Lezcano <daniel.lezcano@free.fr> - 0.6.0
- Reduced spec file

* Sun Aug 3 2008 Daniel Lezcano <dlezcano@fr.ibm.com> - 0.1.0
- Initial RPM release.

# Local variables:
# mode: shell-script
# sh-shell: rpm
# end:
