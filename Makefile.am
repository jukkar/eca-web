
AM_MAKEFLAGS = --no-print-directory

eca_web_sources = \
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
	src/cellular.py

static_sources = \
	src/static/util.js \
	src/static/eca.css \
	src/static/status.png \
	src/static/favicon.ico \
	src/static/help.html

template_sources = \
	src/templates/error.html \
	src/templates/login_error.html \
	src/templates/layout.html \
	src/templates/new_login.html \
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

EXTRA_DIST = \
	COPYING \
	bootstrap \
	bootstrap-configure

eca_webdir = @prefix@
eca_web_SCRIPTS = $(eca_web_sources)

EXTRA_DIST += $(eca_web_sources) $(template_sources) $(static_sources)

eca_web_templatesdir = @prefix@/templates
eca_web_templates_DATA = $(template_sources)

eca_web_staticdir = @prefix@/static
eca_web_static_DATA = $(static_sources)

MAINTAINERCLEANFILES = Makefile.in \
	aclocal.m4 configure config.h.in config.sub config.guess \
	ltmain.sh depcomp compile missing install-sh mkinstalldirs
