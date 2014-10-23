# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           python-softlayer
Version:        773ab17
Release:        1%{?dist}
Summary:        softlayer python interface

License:        Softlayer
URL:            https://github.com/softlayer/softlayer-python
Source0:        python-softlayer-773ab17.tar.gz

#BuildArch:      
BuildRequires:  python-devel
Requires:       python-requests, python-docopt = 0.6.1, python-prettytable >= 0.7.0
Requires:       python-importlib, python-six >= 1.6.1

%description


%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%files
%doc
/usr/bin/sl
# For noarch packages: sitelib
%{python_sitelib}/*
# For arch-specific packages: sitearch
#%{python_sitearch}/*


%changelog
* Wed Mar 19 2014 Andy Bakun <rpmbuild@thwartedefforts.org> 773ab17-1
- initial packaging
