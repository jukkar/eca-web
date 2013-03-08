
AM_MAKEFLAGS = --no-print-directory

eca_web_sources = \
	src/static/util.js \
	src/static/eca.css \
	src/static/status.png \
	src/static/favicon.ico \
	src/rescan.py \
	src/util.py \
	src/config.py \
	src/edit.py \
	src/agent-helper.py \
	src/tethering.py \
	src/view.py \
	src/eca.py \
	src/connect.py \
	src/bluetooth.py \
	src/technology.py \
	src/cellular.py \
	src/templates/error.html \
	src/templates/login_error.html \
	src/templates/layout.html \
	src/templates/login.html \
	src/templates/edit.html \
	src/templates/logout.html \
	src/templates/listing.html \
	src/templates/name.html \
	src/templates/base.html \
	src/templates/property.html \
	src/templates/cellular.html \
	src/templates/login_ok.html \
	src/templates/bt_devices.html \
	src/templates/bluetooth.html \
	src/templates/service.html

EXTRA_DIST = $(eca_web_sources)

eca_webdir = @prefix@
eca_web_SCRIPTS = $(eca_web_sources)

MAINTAINERCLEANFILES = Makefile.in \
	aclocal.m4 configure config.h.in config.sub config.guess \
	ltmain.sh depcomp compile missing install-sh mkinstalldirs
