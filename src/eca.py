import os
import time
import web
from web import form
import view
import config
from util import get_value, get_str_value, get_properties, get_allowed_users, \
    get_dict_value, restyle, is_known_service, is_vpn_service, get_security, \
    is_immutable_service
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
    '/logout', 'Logout',
    '/edit/(.+)', 'Edit',
    '/bluetooth', 'Bluetooth',
    '/cellular', 'Cellular',
)

title = "ECA Configuration"
logout = "ECA Configuration logout"

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

allowed = get_allowed_users()

def logged():
    if session.get("logged_in"):
        return True
    else:
        return False

class Login:
    login_form = form.Form(
        form.Textbox('user', form.notnull, description="Username"),
        form.Password('passwd', form.notnull, description="Password"),
        form.Button('Login', description="Login"),
        )

    def GET(self):
        if logged():
            raise web.seeother("/")
        else:
            return render.login(self.login_form(),
                                "Please authenticate yourself")

    def POST(self):
        if not self.login_form.validates():
            return render.login(self.login_form,
                                "Login failed. Please authenticate yourself")

        username, password = web.input().user, web.input().passwd
        if (username,password) in allowed:
            session.logged_in = True
            return view.main_screen()
        else:
            session.logged_in = False
            return render.login_error()

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
            if not tethering.form.validates():
                return render.base(view.listing(),
                                   title, logout)
            else:
                tethering.update(input)

        elif input.Submit == "technology":
            if not technology.form.validates():
                return render.base(view.listing(),
                                   title, logout)
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
        immutable = is_immutable_service(format(service))
        vpn = is_vpn_service(format(service))
        if is_known_service(format(service)) and not vpn:
            if immutable == True:
                return render.error("Service %s is immutable. Please edit correct config file in /var/lib/connman instead." % format(service))
            update_fields(format(service))
            return render.edit("Edit Service", format(service), edit.form)
        elif vpn:
            if immutable == True:
                return render.error("VPN service %s is immutable. Please edit correct config file in /var/lib/connman-vpn instead." % format(service))
            return render.error("VPN services cannot be edited. Place config file to /var/lib/connman-vpn to provision a VPN service")
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
                return render.error("WPA Enterprise services cannot be edited. Place config file to /var/lib/connmann to provision a 802.1x service")
            else:
                return render.error("Cannot edit service %s %s" % (format(service), securities))

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
        return view.main_screen()

class Cellular:
    def GET(self):
        if not logged():
            raise web.seeother('/login')
        return cellular.view()

    def POST(self):
        if not logged():
            raise web.seeother("/login")
        input = web.input()
        return view.main_screen()

session = web.session.Session(app, web.session.DiskStore('sessions'),
                              initializer={ 'logged_in': False, })

if __name__ == "__main__":
    _dir = os.path.realpath(__file__)
    app.internalerror = web.debugerror
    app.run()

