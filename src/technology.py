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

import dbus
import web
from web import form
from util import get_offlinemode_status, set_offlinemode_status, \
    set_technology_status, add_technology_links

offlinemode = "OFF"
wifi = "ON"
cellular = "ON"
bluetooth = "ON"
wired = "ON"
gadget = "OFF"

form = web.form.Form(
    web.form.Radio('offlinemode', args=["ON", "OFF"],
                   value=offlinemode,
                   description="Flight mode"),
    web.form.Radio('wired', args=["ON", "OFF"],
                   value=wired,
                   description="Wired"),
    web.form.Radio('wifi', args=["ON", "OFF"],
                   value=wifi,
                   description="Wifi"),
    web.form.Radio('cellular', args=["ON", "OFF"],
                   value=cellular,
                   description="Cellular"),
    web.form.Radio('bluetooth', args=["ON", "OFF"],
                   value=bluetooth,
                   description="Bluetooth"),
    web.form.Radio('gadget', args=["ON", "OFF"],
                   value=gadget,
                   description="USB networking"),
    web.form.Button('Submit', value="technology"))

def view():
    rendered = form.render()
    return add_technology_links(rendered,
                                form.get("bluetooth").value,
                                form.get("cellular").value)

def update(input):
    offlinemode_status = get_offlinemode_status()
    if input.offlinemode != offlinemode_status:
        if input.offlinemode == "ON":
            mode = dbus.Boolean(1)
        else:
            mode = dbus.Boolean(0)
        set_offlinemode_status(mode)

    if input.wired != wired:
        set_technology_status("ethernet", input.wired)

    if input.wifi != wifi:
        set_technology_status("wifi", input.wifi)

    if input.cellular != cellular:
        set_technology_status("cellular", input.cellular)

    if input.bluetooth != bluetooth:
        set_technology_status("bluetooth", input.bluetooth)

    if input.gadget != gadget:
        set_technology_status("gadget", input.gadget)
