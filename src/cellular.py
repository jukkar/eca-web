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

