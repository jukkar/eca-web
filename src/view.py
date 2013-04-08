import web
import config
import dbus
from eca import render, title, logout
from util import get_value, get_properties, get_tethering_status, \
    get_offlinemode_status, get_technology_status, get_services
import technology
import tethering
import rescan

def listing(**k):
    return render.listing(get_services())


def main_screen():
    (tethering.wifi, tethering.ssid,
     tethering.passphrase) = get_tethering_status("wifi")
    tethering.ethernet= get_tethering_status("ethernet")
    tethering.bluetooth = get_tethering_status("bluetooth")

    if tethering.wifi== None:
        tethering.wifi = "OFF"

    if tethering.ethernet== None:
        tethering.ethernet = "OFF"

    if tethering.bluetooth == None:
        tethering.bluetooth = "OFF"

    tethering.form.get('ssid').value = tethering.ssid
    tethering.form.get('passphrase').value = tethering.passphrase
    tethering.form.get('wifi').value = tethering.wifi
    tethering.form.get('ethernet').value = tethering.ethernet
    tethering.form.get('bluetooth').value = tethering.bluetooth

    offlinemode_status = get_offlinemode_status()
    if offlinemode_status == True:
        technology.offlinemode = "ON"
    else:
        technology.offlinemode = "OFF"
    technology.form.get('offlinemode').value = technology.offlinemode

    (technology.wired, technology.wifi, technology.ethernet,
     technology.bluetooth) = get_technology_status()
    technology.form.get('wired').value = technology.wired
    technology.form.get('wifi').value = technology.wifi
    technology.form.get('cellular').value = technology.cellular
    technology.form.get('bluetooth').value = technology.bluetooth

    return render.base(listing(),
                       title, logout)
