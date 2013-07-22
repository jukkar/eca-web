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

import web
import config
import dbus
from eca import render, title, logout, help
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

    if tethering.gadget == None:
        tethering.gadget = "OFF"

    tethering.form.get('ssid').value = tethering.ssid
    tethering.form.get('passphrase').value = tethering.passphrase
    tethering.form.get('wifi').value = tethering.wifi
    tethering.form.get('ethernet').value = tethering.ethernet
    tethering.form.get('bluetooth').value = tethering.bluetooth
    tethering.form.get('gadget').value = tethering.gadget

    offlinemode_status = get_offlinemode_status()
    if offlinemode_status == True:
        technology.offlinemode = "ON"
    else:
        technology.offlinemode = "OFF"
    technology.form.get('offlinemode').value = technology.offlinemode

    (technology.wired, technology.wifi, technology.cellular,
     technology.bluetooth, technology.gadget) = get_technology_status()
    technology.form.get('wired').value = technology.wired
    technology.form.get('wifi').value = technology.wifi
    technology.form.get('cellular').value = technology.cellular
    technology.form.get('bluetooth').value = technology.bluetooth
    technology.form.get('gadget').value = technology.gadget

    return render.base(listing(),
                       title, logout, help)
