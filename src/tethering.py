import web
from web import form
from util import set_tethering_status

wifi = "OFF"
ssid = None
passphrase = None
ethernet = "OFF"
bluetooth = "OFF"

form = web.form.Form(
    web.form.Radio('wifi', args=['ON', 'OFF'],
                   value=wifi,
                   description="Activate Wlan tethering"),
    web.form.Textbox('ssid', value=ssid,
                     description="Wlan access point SSID:"),
    web.form.Textbox('passphrase', value=passphrase,
                     description="Wlan access point passphrase:"),
    web.form.Radio('ethernet', args=['ON', 'OFF'],
                   value=ethernet,
                   description="Activate ethernet tethering"),
    web.form.Radio('bluetooth', args=['ON', 'OFF'],
                   value=bluetooth,
                   description="Activate bluetooth tethering"),
    web.form.Button('Submit', value="tethering"))

def view():
    return form.render()

def update(input):
    if input.wifi != wifi:
        set_tethering_status("wifi", input.wifi, input.ssid, input.passphrase)
    if input.ssid != ssid or input.passphrase != passphrase:
        set_tethering_status("wifi", None, input.ssid, input.passphrase)
    if input.ethernet != ethernet:
        set_tethering_status("ethernet", input.ethernet)
    if input.bluetooth != bluetooth:
        set_tethering_status("bluetooth", input.bluetooth)

