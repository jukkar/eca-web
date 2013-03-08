import dbus
import web
from web import form
import eca
from util import get_bt_devices

form = form.Form(
    form.Textbox("pin", class_="textEntry", size=64, description="PIN"),
    form.Button('Submit', value="bluetooth"),
)

def listing(**k):
    #return eca.render.bt_devices(get_bt_devices())
    return eca.render.error("Not implemented yet")

def view():
    return eca.render.bluetooth(listing(), form, "Bluetooth configuration")

