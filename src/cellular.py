import dbus
import web
from web import form
import eca

form = form.Form(
    form.Textbox("pin", class_="textEntry", size=64, description="PIN"),
    form.Button('Submit', value="cellular"),
)

def listing(**k):
    return eca.render.error("Not implemented yet")

def view():
    return eca.render.cellular(listing(), form, "Cellular configuration")

