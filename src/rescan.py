import dbus
import web
from web import form
from util import request_rescan

form = web.form.Form(
    web.form.Button('Submit', value="rescan", html="<b>Rescan</b>"))

def view():
    return form.render()

def update(input):
    request_rescan("wifi")
