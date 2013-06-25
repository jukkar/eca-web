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
from subprocess import Popen, PIPE, STDOUT
from time import sleep
import eca
from util import get_bt_devices, bluetooth_enable_ssp, bluetooth_disable_ssp

agent = None

form = form.Form(
    form.Textbox("pin", form.notnull,
                 form.regexp('^\d+$', 'Not a number.'),
                 class_="textEntry", size=64,
                 description="PIN"),
    form.Button('Submit', type="submit", value="pair", html="Start pairing"),
    form.Button('Submit', type="submit", value="nopin", html="Pair without PIN"),
    form.Button('Submit', type="submit", value="stop_pairing", html="Stop pairing"),
)

def listing(**k):
    return eca.render.bt_help()

def view():
    return eca.render.bluetooth(listing(), form, "Bluetooth configuration")

def setup_agent(use_pin):
    if use_pin == True:
        cap = "KeyboardOnly"
    else:
        cap = "NoInputNoOutput"

    agent = Popen(["%s/agent-helper-bt.py" % eca.dir(), "-c", cap],
                  shell=False, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return agent

def bt_pair(use_pin, pin, agent):
    sleep(1)
    if use_pin == True:
        print >> agent.stdin, "%s\n" % pin
        agent.stdin.flush()
    agent.wait()
    if agent.returncode == 0:
        return True
    else:
        return False

def start_agent(use_pin, pin):
    global agent
    agent = setup_agent(use_pin)
    return bt_pair(use_pin, pin, agent)

def stop_pairing():
    try:
        agent.kill()
    except:
        return False
    bluetooth_enable_ssp("hci0")
    return True

def start_pairing(use_pin, pin):
    # We turn off the secure simple pairing so that the user is able
    # to know the PIN code.
    # TBD: fix the adater name later
    bluetooth_disable_ssp("hci0")
    ret = start_agent(use_pin, pin)
    bluetooth_enable_ssp("hci0")
    return ret
