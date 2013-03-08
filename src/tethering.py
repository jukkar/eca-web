import web
from web import form
from util import set_tethering_status

wifi = "OFF"
ssid = None
passphrase = None
ethernet = "OFF"
bluetooth = "OFF"

vssid = form.regexp(r".{1,32}$", "Must be between 1 and 32 characters")
vpassphrase = form.regexp(r".{8,64}$", "Must be between 8 and 64 characters")

form = web.form.Form(
    web.form.Radio('wifi', args=['ON', 'OFF'],
                   value=wifi,
                   description="Activate WLAN tethering"),
    web.form.Textbox('ssid', vssid, value=ssid,
                     description="WLAN access point SSID:"),
    web.form.Textbox('passphrase', vpassphrase, value=passphrase,
                     description="WLAN access point passphrase:"),
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

