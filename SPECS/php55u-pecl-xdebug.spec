%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?php_extdir: %{expand: %%global php_extdir %(php-config --extension-dir)}}

%define pecl_name xdebug

%global php_base php55u

Name:           %{php_base}-pecl-xdebug
Version:        2.2.3
Release:        2.ius%{?dist}
Summary:        PECL package for debugging PHP scripts

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/xdebug
Source0:        http://pecl.php.net/get/xdebug-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  %{php_base}-devel %{php_base}-pear

# to force use of autoconf and not autoconf26x
%if 0%{?rhel} >= 6
BuildRequires: autoconf
%else
BuildRequires: autoconf < 2.63
%endif

%if 0%{?fedora}
%define config_flags --with-libedit
BuildRequires:  libedit-devel
%else
%define config_flags --without-libedit
%endif

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

Provides:       php-pecl(Xdebug) = %{version}

%if 0%{?php_zend_api}
Requires:       %{php_base}(zend-abi) = %{php_zend_api}
Requires:       %{php_base}(api) = %{php_core_api}
%else
Requires:       %{php_base}-api = %{php_apiver}
%endif

%description
The Xdebug extension helps you debugging your script by providing a lot
of valuable debug information.


%prep
%setup -qcn xdebug-%{version}
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pecl_name}-%{version}/%{pecl_name}.xml
cd xdebug-%{version}

# fix rpmlint warnings
#iconv -f iso8859-1 -t utf-8 Changelog > Changelog.conv && mv -f Changelog.conv Changelog
#chmod -x *.[ch]


%build
cd xdebug-%{version}
phpize
%configure --enable-xdebug
CFLAGS="$RPM_OPT_FLAGS" make

# Build debugclient
pushd debugclient
cp %{_datadir}/automake*/depcomp .
chmod +x configure
%configure %{config_flags}
CFLAGS="$RPM_OPT_FLAGS" make
popd


%install
cd xdebug-%{version}
rm -rf $RPM_BUILD_ROOT
make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install debugclient
install -d $RPM_BUILD_ROOT%{_bindir}
install -pm 755 debugclient/debugclient $RPM_BUILD_ROOT%{_bindir}

# install config file
install -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/php.d/xdebug.ini << 'EOF'
; Enable xdebug extension module
zend_extension=%{php_extdir}/xdebug.so
EOF

# install doc files
install -d docs
install -pm 644 CREDITS LICENSE NEWS README docs

# Install XML package description
install -d $RPM_BUILD_ROOT%{pecl_xmldir}
install -pm 644 %{pecl_name}.xml $RPM_BUILD_ROOT%{pecl_xmldir}/%{name}.xml


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc xdebug-%{version}/docs/*
%config(noreplace) %{_sysconfdir}/php.d/xdebug.ini
%{php_extdir}/xdebug.so
%{_bindir}/debugclient
%{pecl_xmldir}/%{name}.xml


%changelog
* Fri Jan 24 2014 Ben Harper <ben.harper@rackspace.com> - 2.2.3-2.ius
- porting from php54-pecl-xdebug

* Wed May 22 2013 Ben Harper <ben.harper@rackspace.com> - 2.2.3-1.ius
- Latest sources from upstream

* Mon Mar 25 2013 Ben Harper <ben.harper@rackspace.com> - 2.2.2-1.ius
- Latest sources from upstream

* Tue Aug 21 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> - 2.2.1-2
- Rebuilding against php54-5.4.6-2.ius as it is now using bundled PCRE.

* Mon Jul 16 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> 2.2.1-1
- Latest sources from upstream

* Fri May 11 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> 2.2.0-2
- Build for php54

* Wed May 05 2012 Dustin Henry Offutt <dustin.offutt@rackspace.com> 2.2.0-1
- Latest sources from upstream
- Remove expectation of file "Changelog" which file "NEWS" now covers, according to the pecl-xdebug project (http://bugs.xdebug.org/view.php?id=828)

* Wed Mar 14 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.1.4-1
- Latest sources from upstream

* Thu Jan 26 2012 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.1.3-1
- Latest sources from upstream

* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.1.2-2
- Rebuilding

* Fri Jul 29 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.1.2-1
- Latest sources from upstream

* Mon Apr 4 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.1.1-1
- Latest sources from upstream
- Removed Patch0: %%{pecl_name}-2.0.3-codecoverage.patch

* Mon Jan 24 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> 2.0.5-2
- Porting from EPEL to IUS

* Mon Sep 14 2009 Christopher Stone <chris.stone@gmail.com> 2.0.5-1.1
- Upstream sync

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 2.0.4-1
- update to 2.0.4 (bugfix + Basic PHP 5.3 support)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-4
- Add code coverage patch (bz #460348)
- http://bugs.xdebug.org/bug_view_page.php?bug_id=0000344

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-3
- Revert last change

* Thu Oct 09 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-2
- Add php-xml to Requires (bz #464758)

* Thu May 22 2008 Christopher Stone <chris.stone@gmail.com> 2.0.3-1
- Upstream sync
- Clean up libedit usage
- Minor rpmlint fix

* Sun Mar 02 2008 Christopher Stone <chris.stone@gmail.com> 2.0.2-4
- Add %%{__pecl} to post/postun Requires

* Fri Feb 22 2008 Christopher Stone <chris.stone@gmail.com> 2.0.2-3
- %%define %%pecl_name to properly register package
- Install xml package description
- Add debugclient
- Many thanks to Edward Rudd (eddie@omegaware.com) (bz #432681)

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.0.2-2
- Autorebuild for GCC 4.3

* Sun Nov 25 2007 Christopher Stone <chris.stone@gmail.com> 2.0.2-1
- Upstream sync

* Sun Sep 30 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-2
- Update to latest standards
- Fix encoding on Changelog

* Sat Sep 08 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-1
- Upstream sync
- Remove %%{?beta} tags

* Sun Mar 11 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.5.RC2
- Create directory to untar sources
- Use new ABI check for FC6
- Remove %%{release} from Provides

* Mon Jan 29 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.4.RC2
- Compile with $RPM_OPT_FLAGS
- Use $RPM_BUILD_ROOT instead of %%{buildroot}
- Fix license tag

* Mon Jan 15 2007 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.3.RC2
- Upstream sync

* Sun Oct 29 2006 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.2.RC1
- Upstream sync

* Wed Sep 06 2006 Christopher Stone <chris.stone@gmail.com> 2.0.0-0.1.beta6
- Remove Provides php-xdebug
- Fix Release
- Remove prior changelog due to Release number change
