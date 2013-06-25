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
from util import get_service

vpassphrase = form.regexp(r".{8,64}$", "Must be between 8 and 64 characters")
psk_form = web.form.Form(
    form.Hidden('servicetype'),
    form.Password("passphrase", autocomplete="off",
                  description="Passphrase"),
    form.Password("passphrase2", autocomplete="off",
                  description="Repeat passphrase"),
    form.Button("Submit", type="submit", value="new_psk"),
    validators = [
        form.Validator("Passphrase do not match",
                       lambda i: i.passphrase == i.passphrase2)
        ]
)

wep_form = web.form.Form(
    form.Hidden('servicetype'),
    form.Password("passphrase", autocomplete="off",
                  description="Passphrase"),
    form.Password("passphrase2", autocomplete="off",
                  description="Repeat passphrase"),
    form.Button("Submit", type="submit", value="new_wep"),
    validators = [
        form.Validator("Passphrase do not match",
                       lambda i: i.passphrase == i.passphrase2)
        ]
)

def setup_agent():
    agent = Popen(["%s/agent-helper.py" % eca.dir()], shell=False,
                  stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return agent

def connect_psk(input, service_id, agent):
    (from_agent, to_agent, agent_stderr) = (agent.stdout, agent.stdin,
                                            agent.stderr)
    sleep(1)
    print >> to_agent, "Passphrase=%s\n" % input.passphrase
    to_agent.flush()
    sleep(1)
    service = get_service(service_id)
    try:
        service.Connect()
    except dbus.DBusException, error:
        #print "%s: %s" % (error._dbus_error_name, error.message)

        if error._dbus_error_name != "net.connman.Error.InProgress":
            agent.terminate()
            agent.wait()
            return "Invalid or missing service %s (%s: %s)" % \
                (service_id, error._dbus_error_name, error.message)

    sleep(3)
    agent.terminate()
    agent.wait()
    return None


def service_psk(input, service_id):
    # Setup agent which waits password query
    agent = setup_agent()
    return connect_psk(input, service_id, agent)

def service_wep(input, service_id):
    agent = setup_agent()
    return connect_psk(input, service_id, agent)

def service(input, service_id):
    service = get_service(service_id)
    try:
        service.Connect()
    except dbus.DBusException, error:
        print "%s: %s" % (error._dbus_error_name, error.message)

def disconnect_service(input, service_id):
    service = get_service(service_id)
    try:
        service.Disconnect()
    except dbus.DBusException, error:
        return error
    return None
