#
# ECA web UI
#
# Copyright (C) 2013  Intel Corporation. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import time
import crypt, uuid
import web
from web import form
import view
import config
from util import get_value, get_str_value, get_properties, get_allowed_users, \
    get_dict_value, restyle, is_known_service, is_vpn_service, get_security, \
    is_immutable_service, is_cellular_service, get_service_type, \
    set_root_password, set_bt_discoverable, set_cellular_pin, \
    activate_cellular
import technology
import tethering
import rescan
import edit
from edit import update_fields
import connect
import bluetooth
import cellular

web.config.debug = False

_dir = "."

def dir():
    return _dir

urls = (
    '/', 'Index',
    '/login', 'Login',
    '/new_login', 'NewLogin',
    '/logout', 'Logout',
    '/edit/(.+)', 'Edit',
    '/bluetooth', 'Bluetooth',
    '/cellular', 'Cellular',
)

title = "ECA Configuration"
logout = "Logout"
help = "Help"

t_globals = {
    'get_value' : get_value,
    'get_str_value' : get_str_value,
    'get_properties' : get_properties,
    'get_dict_value' : get_dict_value,
    'restyle': restyle,
    'view_tethering': tethering.view,
    'view_technology': technology.view,
    'view_rescan': rescan.view,
}

render = web.template.render('templates/', base='layout',
                             cache = config.cache,
                             globals = t_globals)
render._keywords['globals']['render'] = render

app = web.application(urls, globals())

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'),
                                  initializer={ 'logged_in': False, })
    web.config._session = session
else:
    session = web.config._session

allowed_users_file = "/etc/eca-web/users"

allowed = get_allowed_users(allowed_users_file)

def is_allowed():
    global allowed
    if allowed:
        return True
    else:
        allowed = get_allowed_users(allowed_users_file)
        if allowed:
            return True
        return False

def logged():
    if session.get("logged_in"):
        return True
    else:
        return False

new_login_form = form.Form(
    form.Textbox('newuser', form.notnull, description="Web UI username"),
    form.Password('newpasswd', form.notnull, description="Web UI password"),
    form.Password('root_passwd', form.notnull, description="Root user password"),
    form.Password('root_newpasswd', form.notnull, description="Root user password again"),
    form.Button('create', description="Create user"),
    validators = [ form.Validator("Root user passwords did not match.",
                               lambda i: i.root_passwd == i.root_newpasswd)],
    )

class Login:
    login_form = form.Form(
        form.Textbox('user', form.notnull, description="Web Username"),
        form.Password('passwd', form.notnull, description="Web Password"),
        form.Button('Login', description="Login"),
        )

    def GET(self):
        name_ok = is_allowed()
        if name_ok and logged():
            raise web.seeother("/")
        else:
            if not name_ok:
                return render.new_login(new_login_form(),
                                        "Create a username for yourself and set the root user password")
            return render.login(self.login_form(),
                                "Please authenticate yourself")

    def POST(self):
        if is_allowed() and logged():
            raise web.seeother("/")
        if not self.login_form.validates():
            return render.login(self.login_form,
                                "Login failed. Please authenticate yourself")

        username, password = web.input().user, web.input().passwd
        salt = ""
        password_without_hash = ""
        for userpwd in allowed:
            (allowed_username, hashed_password) = userpwd
            if username == allowed_username:
                split_password = hashed_password.rsplit("$", 1)
                salt = split_password[0] + "$"
                password_without_hash = split_password[1]
                break
        hashed_password = crypt.crypt(password, salt)
        if (username, hashed_password) in allowed:
            session.logged_in = True
            return view.main_screen()
        else:
            session.logged_in = False
            return render.login_error()

class NewLogin:
    def POST(self):
        if not new_login_form.validates():
            return render.new_login(new_login_form,
                                "Cannot validate your credentials, try again.")

        msg = set_root_password(web.input().root_passwd)
        if msg != "":
            return render.new_login(new_login_form, msg)

        f = open(allowed_users_file,'w')
        salt = "$6$" + uuid.uuid4().hex + "$"
        hashed_password = crypt.crypt(web.input().newpasswd, salt)

        f.write(web.input().newuser + " " + hashed_password + "\n")
        f.close()
        allowed = get_allowed_users(allowed_users_file)
        raise web.seeother('/login')

class Logout:
    def GET(self):
        session.logged_in = False
        session.kill()
        raise web.seeother('/login')

class Index:
    def GET(self):
        if not logged():
            raise web.seeother('/login')

        return view.main_screen()

    def POST(self):
        if not logged():
            raise web.seeother("/login")
        input = web.input()
        if input.Submit == "tethering":
            if input["wifi"] == "ON":
                # Only validating the form if Wlan tethering is turned ON
                input.valid = True

                try:
                    len_passphrase = len(input["passphrase"])
                except:
                    len_passphrase = 0;

                try:
                    len_ssid = len(input["ssid"])
                except:
                    len_ssid = 0;

                if len_ssid == 0:
                    tethering.form.note = "Wlan SSID missing"
                    input.valid = False
                elif len_passphrase < 8 or len_passphrase > 64:
                    tethering.form.note = "Passphrase must be between 8 and 64 characters"
                    input.valid = False

                if not input.valid:
                    return render.base(view.listing(),
                                       title, logout, help)
                else:
                    tethering.form.note = ""
                    tethering.update(input)
            else:
                tethering.form.note = ""
                tethering.update(input)

        elif input.Submit == "technology":
            if not technology.form.validates():
                return render.base(view.listing(),
                                   title, logout, help)
            else:
                technology.update(input)

        elif input.Submit == "rescan":
            rescan.update(input)
            # allow some time for the scan to return some results
            time.sleep(6)

        return view.main_screen()

class Edit:
    def GET(self, service):
        if not logged():
            raise web.seeother("/login")
        servicetype = get_service_type(format(service))
        edit.form.get("servicetype").value = servicetype
        connect.psk_form.get("servicetype").value = servicetype
        connect.wep_form.get("servicetype").value = servicetype
        immutable = is_immutable_service(format(service))
        vpn = is_vpn_service(format(service))
        if is_known_service(format(service)) and not vpn:
            if immutable == True:
                return render.error("Service %s is immutable." % format(service),
                                    "Please edit correct config file in <samp>/var/lib/connman</samp> instead.")

            update_fields(format(service))
            return render.edit("Edit Service", format(service), edit.form)
        elif vpn:
            if immutable == True:
                return render.error("VPN service <samp>%s</samp> is immutable."  % format(service),
                                    "Please edit correct config file in <samp>/var/lib/connman-vpn</samp> instead.")
            return render.error("VPN services cannot be edited.",
                                "Place config file to <samp>/var/lib/connman-vpn</samp> to provision a VPN service.",
                                "See <a href='http://git.kernel.org/cgit/network/connman/connman.git/tree/doc/vpn-config-format.txt'>config file format specification</a> for details.")

        else:
            securities = get_security(format(service))
            if "psk" in securities:
                return render.edit("Connect Service", format(service),
                                   connect.psk_form)
            elif "none" in securities:
                update_fields(format(service))
                return render.edit("Connect Service", format(service),
                                   edit.form)
            elif "wep" in securities:
                return render.edit("Connect Service", format(service),
                                   connect.wep_form)
            elif "ieee8021x" in securities:
                return render.error("WPA Enterprise services cannot be edited.",
                                    "Place config file to <samp>/var/lib/connman</samp> to provision a 802.1x service.",
                                    "See <a href='http://git.kernel.org/cgit/network/connman/connman.git/tree/doc/config-format.txt'>config file format specification</a> for details.")
            else:
                if servicetype == "cellular":
                    return render.edit("Edit Cellular Service",
                                       format(service),
                                       edit.form)

                return render.error("Cannot edit service <samp>%s</samp> <samp>%s</samp>" % (format(service), securities))

    def POST(self, service):
        if not logged():
            raise web.seeother("/login")
        input = web.input()
        if input.Submit == "edit":
            if not edit.form.validates():
                return render.edit("Edit Service", format(service), edit.form)
            err = edit.update_service(input, format(service))
            if err != None:
                return render.error(err)
        elif input.Submit == "remove":
            err = edit.remove_service(input, format(service))
            if err != None:
                return render.error(err)
        elif input.Submit == "connect":
            err = connect.service(input, format(service))
            if err != None:
                return render.error(err)
        elif input.Submit == "disconnect":
            err = connect.disconnect_service(input, format(service))
            if err != None:
                return render.error("Disconnect failed", err._dbus_error_name,
                                    err.message)
        elif input.Submit == "new_psk":
            if input.passphrase == "":
                return render.edit("Connect Service", format(service),
                                   connect.psk_form)
            err = connect.service_psk(input, format(service))
            if err != None:
                return render.error(err)
        elif input.Submit == "new_wep":
            if input.passphrase == "":
                return render.edit("Connect Service", format(service),
                                   connect.wep_form)
            err = connect.service_wep(input, format(service))
            if err != None:
                return render.error(err)

        raise web.seeother("/")

class Bluetooth:
    def GET(self):
        if not logged():
            raise web.seeother('/login')
        return bluetooth.view()

    def POST(self):
        if not logged():
            raise web.seeother("/login")
        input = web.input()

        if input.Submit == "stop_pairing":
            set_bt_discoverable(False)
            if bluetooth.stop_pairing() == True:
                return render.error("Pairing stopped")
            return render.error("Pairing process could not be stopped. Wait for timeout to happen.")

	# Set the bluetooth device as discoverable so that we can find
	# it while pairing
        error = set_bt_discoverable(True)
        if error == None:
            if input.pin != "":
                use_pin = True
            else:
                use_pin = False

            status = bluetooth.start_pairing(use_pin, input.pin)
            set_bt_discoverable(False)
        else:
            return render.error("%s: %s" % (error._dbus_error_name, error.message))
        if status == False:
            return render.error("Pairing failed")
        return view.main_screen()

class Cellular:
    def GET(self):
        if not logged():
            raise web.seeother('/login')
        return cellular.view()

    def POST(self):
        if not logged():
            raise web.seeother("/login")
        if not cellular.form.validates():
            return cellular.view()

        input = web.input()

        (error, modem) = set_cellular_pin(input.pin)
        if error != None:
            return render.error("Setting PIN failed.<br>%s: %s" % (error._dbus_error_name, error.message))

        (error, text) = activate_cellular()
        if error != None:
            return render.error("Activating cellular context failed. %s: %s" % (error._dbus_error_name, error.message))
        if text != None:
            return render.error(text)
        return view.main_screen()


session = web.session.Session(app, web.session.DiskStore('sessions'),
                              initializer={ 'logged_in': False, })

if __name__ == "__main__":
    _dir = os.path.realpath(__file__)
    #app.internalerror = web.debugerror
    app.run()

