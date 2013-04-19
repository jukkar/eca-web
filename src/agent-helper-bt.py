#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

import gobject

import sys
import errno
import dbus
import dbus.service
import dbus.mainloop.glib
from optparse import OptionParser
import bluezutils

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/eca/agent"

bus = None
device_obj = None
dev_path = None

# how long we wait (in ms)
TIMEOUT = 120000

exit_code = 0

def print_err(*args):
	msg = ' '.join(map(str,args)) + '\n'
	sys.stderr.write(msg)
	#syslog.syslog(msg)

def quit_handler():
	# TBD: Check whether the pairing succeed or not
	exit_code = 0
	mainloop.quit()

def launch_quit():
	gobject.timeout_add(1000, quit_handler)

def ask(stdin):
    out = ''
    while True:
        inchar = stdin.read(1)
        if inchar != None and inchar != '\n':
            out = out + str(inchar)
        else:
            break
    launch_quit()
    return out

def set_trusted(path):
	props = dbus.Interface(bus.get_object("org.bluez", path),
					"org.freedesktop.DBus.Properties")
	props.Set("org.bluez.Device1", "Trusted", True)

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	exit_on_release = True

	def set_exit_on_release(self, exit_on_release):
		self.exit_on_release = exit_on_release

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Release(self):
		print_err("Release")
		if self.exit_on_release:
			mainloop.quit()

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		print_err("AuthorizeService (%s, %s)" % (device, uuid))
		# currently we always authorize
		authorize = "yes"
		if (authorize == "yes"):
			return
		raise Rejected("Connection rejected by user")

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print_err("RequestPinCode (%s)" % (device))
		set_trusted(device)
		return ask(sys.stdin)

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		print_err("RequestPasskey (%s)" % (device))
		set_trusted(device)
		passkey = ask(sys.stdin)
		return dbus.UInt32(passkey)

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="ouq", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		print_err("DisplayPasskey (%s, %06u entered %u)" %
						(device, passkey, entered))

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="os", out_signature="")
	def DisplayPinCode(self, device, pincode):
		print_err("DisplayPinCode (%s, %s)" % (device, pincode))

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		print_err("RequestConfirmation (%s, %06d)" % (device, passkey))
		raise Rejected("Confirmation rejected, cannot ask user")

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="o", out_signature="")
	def RequestAuthorization(self, device):
		print_err("RequestAuthorization (%s)" % (device))
		raise Rejected("Pairing rejected, cannot ask user")

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Cancel(self):
		print_err("Cancel")

def pair_reply():
	print_err("Device paired")
	set_trusted(dev_path)
	mainloop.quit()

def pair_error(error):
	err_name = error.get_dbus_name()
	if err_name == "org.freedesktop.DBus.Error.NoReply" and device_obj:
		print_err("Timed out. Cancelling pairing")
		device_obj.CancelPairing()
	else:
		print_err("Creating device failed: %s" % (error))

	mainloop.quit()

def timeout_handler():
	exit_code = -errno.ETIMEDOUT
	mainloop.quit()

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()

	capability = "KeyboardDisplay"

	parser = OptionParser()
	parser.add_option("-i", "--adapter", action="store",
					type="string",
					dest="adapter_pattern",
					default=None)
	parser.add_option("-c", "--capability", action="store",
					type="string", dest="capability")
	parser.add_option("-t", "--timeout", action="store",
					type="int", dest="timeout",
					default=TIMEOUT)
	(options, args) = parser.parse_args()
	if options.capability:
		capability  = options.capability

	path = "/eca/agent"
	agent = Agent(bus, path)

	mainloop = gobject.MainLoop()

	obj = bus.get_object(BUS_NAME, "/org/bluez");
	manager = dbus.Interface(obj, "org.bluez.AgentManager1")
	manager.RegisterAgent(path, capability)

	print_err("Agent registered")

	# Fix-up old style invocation (BlueZ 4)
	if len(args) > 0 and args[0].startswith("hci"):
		options.adapter_pattern = args[0]
		del args[:1]

	if len(args) > 0:
		device = bluezutils.find_device(args[0],
						options.adapter_pattern)
		dev_path = device.object_path
		agent.set_exit_on_release(False)
		device.Pair(reply_handler=pair_reply, error_handler=pair_error,
								timeout=TIMEOUT)
		device_obj = device
	else:
		gobject.timeout_add(TIMEOUT, timeout_handler)
		manager.RequestDefaultAgent(path)

	mainloop.run()
	sys.exit(exit_code)
