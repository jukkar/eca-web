#!/usr/bin/python

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib
import sys

class Canceled(dbus.DBusException):
	_dbus_error_name = "net.connman.Error.Canceled"

class LaunchBrowser(dbus.DBusException):
	_dbus_error_name = "net.connman.Agent.Error.LaunchBrowser"

def print_err(*args):
	msg = ' '.join(map(str,args)) + '\n'
	sys.stderr.write(msg)

def read_answer(stdin):
    out = ''
    while True:
        inchar = stdin.read(1)
        if inchar != None and inchar != '\n':
            out = out + str(inchar)
        else:
            break
    return out

class Agent(dbus.service.Object):
	name = None
	ssid = None
	identity = None
	passphrase = None
	wpspin = None
	username = None
	password = None

	@dbus.service.method("net.connman.Agent",
					in_signature='', out_signature='')
	def Release(self):
		mainloop.quit()

	def input_passphrase(self):
		response = {}

		if not self.identity and not self.passphrase and not self.wpspin:
			args = read_answer(sys.stdin)
			#print_err("answer is \"%s\"" % args)
			for arg in args.split():
				if arg.startswith("cancel"):
					response["Error"] = arg
				if arg.startswith("Identity="):
					identity = arg.replace("Identity=", "", 1)
					response["Identity"] = identity
				if arg.startswith("Passphrase="):
					passphrase = arg.replace("Passphrase=", "", 1)
					response["Passphrase"] = passphrase
				if arg.startswith("WPS="):
					wpspin = arg.replace("WPS=", "", 1)
					response["WPS"] = wpspin
					break
		else:
			if self.identity:
				response["Identity"] = self.identity
			if self.passphrase:
				response["Passphrase"] = self.passphrase
			if self.wpspin:
				response["WPS"] = self.wpspin

		gobject.timeout_add(0, self.Release)
		return response

	def input_username(self):
		response = {}

		if not self.username and not self.password:
			args = read_answer()

			for arg in args.split():
				if arg.startswith("cancel") or arg.startswith("browser"):
					response["Error"] = arg
				if arg.startswith("Username="):
					username = arg.replace("Username=", "", 1)
					response["Username"] = username
				if arg.startswith("Password="):
					password = arg.replace("Password=", "", 1)
					response["Password"] = password
		else:
			if self.username:
				response["Username"] = self.username
			if self.password:
				response["Password"] = self.password

		return response

	def input_hidden(self):
		response = {}

		if not self.name and not self.ssid:
			args = read_answer()

			for arg in args.split():
				if arg.startswith("Name="):
					name = arg.replace("Name=", "", 1)
					response["Name"] = name
					break
				if arg.startswith("SSID="):
					ssid = arg.replace("SSID", "", 1)
					response["SSID"] = ssid
					break
		else:
			if self.name:
				response["Name"] = self.name
			if self.ssid:
				response["SSID"] = self.ssid

		return response

	@dbus.service.method("net.connman.Agent",
					in_signature='oa{sv}',
					out_signature='a{sv}')
	def RequestInput(self, path, fields):
		print_err("RequestInput (%s,%s)" % (path, fields))

		response = {}

		if fields.has_key("Name"):
			response.update(self.input_hidden())
		if fields.has_key("Passphrase"):
			response.update(self.input_passphrase())
		if fields.has_key("Username"):
			response.update(self.input_username())

		if response.has_key("Error"):
			if response["Error"] == "cancel":
				raise Canceled("canceled")
				return
			if response["Error"] == "browser":
				raise LaunchBrowser("launch browser")
				return

		#print "returning (%s)" % (response)

		return response

	@dbus.service.method("net.connman.Agent",
					in_signature='os',
					out_signature='')
	def RequestBrowser(self, path, url):
		print_err("RequestBrowser (%s,%s)" % (path, url))
		raise Canceled("canceled")
		return

	@dbus.service.method("net.connman.Agent",
					in_signature='os',
					out_signature='')
	def ReportError(self, path, error):
		print_err("ReportError %s, %s" % (path, error))
		return


	@dbus.service.method("net.connman.Agent",
					in_signature='', out_signature='')
	def Cancel(self):
		mainloop.quit()

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object('net.connman', "/"),
					'net.connman.Manager')

	path = "/eca/agent"
	object = Agent(bus, path)

	try:
		manager.RegisterAgent(path)
	except:
		print_err("Cannot register ConnMan agent.")
		sys.exit()

	mainloop = gobject.MainLoop()
	mainloop.run()
