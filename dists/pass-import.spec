# pass import - Passwords importer swiss army knife
# Copyright (C) 2017-2026 Alexandre Pujol <alexandre@pujol.io>
# SPDX-License-Identifier: GPL-3.0-or-later

# Warning: for development only.

Name:           pass-import
Version:        3.5
Release:        1%{?dist}
Summary:        A pass extension for importing data from most existing password managers
License:        GPL-3.0-or-later
URL:            https://github.com/roddhjav/pass-import
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

%if 0%{?suse_version}
Requires:       password-store
Requires:       python3-PyYAML
Recommends:     python3-SecretStorage
Recommends:     python3-python-magic
Recommends:     python3-zxcvbn-rs-py
BuildRequires:  python-rpm-macros
%else
Requires:       pass
Requires:       python3-pyyaml
Recommends:     python3-secretstorage
Recommends:     python3-magic
BuildRequires:  python3-devel
%endif
Requires:       python3-requests
Recommends:     python3-defusedxml
Recommends:     python3-pykeepass
Recommends:     python3-cryptography
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-setuptools
BuildRequires:  just

%description
A pass extension for importing data from most of the existing password
manager. It also provides the pimport script to support other password
managers as destination.

%prep
%autosetup

%build
just python=%{__python3} build

%install
just python=%{__python3} destdir="%{buildroot}" install

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/pimport
%{python3_sitelib}/pass_import/
%{python3_sitelib}/pass_import-%{version}.dist-info/
%{_prefix}/lib/password-store/extensions/import.bash
%{_mandir}/man1/pass-import.1*
%{_mandir}/man1/pimport.1*
%{_datadir}/bash-completion/completions/pass-import
%{_datadir}/bash-completion/completions/pimport
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_pass-import
%{_datadir}/zsh/site-functions/_pimport

%changelog
