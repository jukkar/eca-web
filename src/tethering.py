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
from web import form
from util import set_tethering_status

wifi = "OFF"
ssid = None
passphrase = None
ethernet = "OFF"
bluetooth = "OFF"
gadget = "OFF"

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
    web.form.Radio('gadget', args=['ON', 'OFF'],
                   value=gadget,
                   description="Activate USB tethering"),
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
    if input.gadget != gadget:
        set_tethering_status("gadget", input.gadget)

