import dbus
import web
from web import form
import eca

form = form.Form(
    form.Textbox("pin", form.notnull, class_="textEntry", size=64,
                 description="PIN"),
    form.Button('Submit', type="submit", value="cellular"),
)

def listing(**k):
    return eca.render.cellular_help()

def view():
    return eca.render.cellular(listing(), form, "Cellular configuration")

