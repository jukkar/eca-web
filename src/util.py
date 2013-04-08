import dbus
import re

def get_allowed_users(filename):
	try:
		with open(filename) as f:
			content = f.readlines()
	except:
		return []

	f.close()

	users = []
	for line in content:
		if line.startswith("#"):
			next
		splitted = line.rstrip('\n').split(" ", 1)
		try:
			users.append((splitted[0], splitted[1]))
		except:
			return []
	return users

def extract_values(values):
	val = "{"
	for key in values.keys():
		val += " " + key + "="
		if key in ["PrefixLength"]:
			val += "%s" % (int(values[key]))
		else:
			if key in ["Servers", "Excludes"]:
				val += extract_list(values[key])
			else:
				val += str(values[key])
	val += " }"
	return val

def extract_list(list):
	val = "["
	for i in list:
		val += " " + str(i)
	val += " ]"
	return val


def get_value(properties, key):
        if key in ["IPv4", "IPv4.Configuration",
                   "IPv6", "IPv6.Configuration",
                   "Proxy", "Proxy.Configuration",
                   "Ethernet", "Provider"]:
            val = extract_values(properties[key])
        elif key in ["Nameservers", "Nameservers.Configuration",
                     "Domains", "Domains.Configuration",
                     "Timeservers", "Timeservers.Configuration",
                     "Security"]:
            val = extract_list(properties[key])
        elif key in ["Favorite", "Immutable", "AutoConnect",
                     "LoginRequired", "PassphraseRequired"]:
            if properties[key] == dbus.Boolean(1):
                val = "true"
            else:
                val = "false"
        elif key in ["Strength"]:
            val = int(properties[key])
        else:
            try:
		    val = properties[key]
	    except:
		    val = "<unknown>"
        return val

def get_str_value(properties, key):
	value = get_value(properties, key)
	if value == "<unknown>":
		return ""
	else:
		return str(value).translate(None, "[]{}").strip()

def get_raw_value(properties, key):
	try:
		val = properties[key]
	except:
		val = None
	return val

def get_dict_value(properties, key, value):
    try:
        return get_raw_value(properties, key)[value]
    except:
        return ""

def get_service(service_id):
	bus = dbus.SystemBus()
	path = "/net/connman/service/" + service_id
	service = dbus.Interface(bus.get_object("net.connman", path),
				 "net.connman.Service")
	return service

def get_services():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("net.connman", "/"),
				 "net.connman.Manager")
	return manager.GetServices()

def get_properties(service_id):
	service = get_service(service_id)
	try:
		return service.GetProperties()
	except:
		return {}

def get_technology_properties():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("net.connman", "/"),
					"net.connman.Manager")
        return manager.GetTechnologies()

def get_offlinemode_status():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("net.connman", "/"),
					"net.connman.Manager")
        return manager.GetProperties()["OfflineMode"]

def set_offlinemode_status(new_mode):
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("net.connman", "/"),
					"net.connman.Manager")
        return manager.SetProperty("OfflineMode", new_mode)

def get_tethering_status(technology_type):
	tech_path = "/net/connman/technology/" + technology_type
	for path, properties in get_technology_properties():
		if path == tech_path:
			if properties["Tethering"] == dbus.Boolean(True):
				status = "ON"
			else:
				status = "OFF"

			if technology_type == "wifi":
				return (status,
					properties["TetheringIdentifier"],
					properties["TetheringPassphrase"])
			else:
				return status

	if technology_type == "wifi":
		return (None, "", "")
	return None

def set_tethering_status(technology_type, new_status, ssid = None,
			 passphrase = None):
	path = "/net/connman/technology/" + technology_type
	bus = dbus.SystemBus()
	technology = dbus.Interface(bus.get_object("net.connman", path),
					"net.connman.Technology")
	if new_status != None:
		if new_status == "ON":
			mode = dbus.Boolean(True)
		else:
			mode = dbus.Boolean(False)

	if technology_type == "wifi":
		if ssid != None:
			try:
				technology.SetProperty("TetheringIdentifier", ssid)
			except:
				pass
		if passphrase != None:
			try:
				technology.SetProperty("TetheringPassphrase", passphrase)
			except:
				pass

	if new_status != None:
		try:
			technology.SetProperty("Tethering", mode)
		except:
			pass


def get_technology_status(technology_type = None):
	if technology_type != None:
		tech_path = "/net/connman/technology/" + technology_type
	else:
		wired_path = "/net/connman/technology/ethernet"
		wifi_path = "/net/connman/technology/wifi"
		cellular_path = "/net/connman/technology/cellular"
		bluetooth_path = "/net/connman/technology/bluetooth"
		tech_path = ""
		status_wired = status_wifi = status_cellular = \
		    status_bluetooth = "OFF"
	for path, properties in get_technology_properties():
		if path == tech_path:
			if properties["Powered"] == dbus.Boolean(True):
				status = "ON"
			else:
				status = "OFF"
			return status
		else:
			if path == wifi_path:
				if properties["Powered"] == dbus.Boolean(True):
					status_wifi = "ON"
				else:
					status_wifi = "OFF"
			elif path == wired_path:
				if properties["Powered"] == dbus.Boolean(True):
					status_wired = "ON"
				else:
					status_wired = "OFF"
			elif path == cellular_path:
				if properties["Powered"] == dbus.Boolean(True):
					status_cellular = "ON"
				else:
					status_cellular = "OFF"
			elif path == bluetooth_path:
				if properties["Powered"] == dbus.Boolean(True):
					status_bluetooth = "ON"
				else:
					status_bluetooth = "OFF"

	return (status_wired, status_wifi, status_cellular, status_bluetooth)

def set_technology_status(technology_type, new_status):
	path = "/net/connman/technology/" + technology_type
	bus = dbus.SystemBus()
	technology = dbus.Interface(bus.get_object("net.connman", path),
					"net.connman.Technology")
	if new_status == "ON":
		mode = dbus.Boolean(True)
	else:
		mode = dbus.Boolean(False)

	try:
		technology.SetProperty("Powered", mode)
	except:
		pass

def split_lines(lines):
	return iter(lines.splitlines())

def restyle(content):
	# add id field to <tr> so that we can disable rows if necessary
	i = 0
	lines = list(split_lines(content))
	for line in lines:
		id = re.search("label for=\"(.+?)\"\>", line)
		if id == None:
			id_str = "no"
		else:
			id_str = line[id.start()+11:id.end()-2]
		lines[i] = line.replace("<tr>",
					"<tr id=\"" + id_str + "-id\">")
		i = i + 1
	return "\n".join(lines)

def add_technology_links(content, bt, cellular):
	# add link to label field so that we can edit the tech if necessary
	i = 0
	lines = list(split_lines(content))
	for line in lines:
		reg = re.search("<tr><th><label for=\"(.+)?\"\>(.+)?\<\/label\>(.*)", line)
		if reg != None:
			tech = reg.group(1)
			if tech == "bluetooth" and bt == "ON":
				name = reg.group(2)
				rest = reg.group(3)
				lines[i] = "<tr><th><label for=\"" + tech + \
				    "\"><a href=\"/" + tech + "\">" + \
				    name + "</a></label>" + rest
				i = i + 1
				continue
			if tech == "cellular" and cellular == "ON":
				name = reg.group(2)
				rest = reg.group(3)
				lines[i] = "<tr><th><label for=\"" + tech + \
				    "\"><a href=\"/" + tech + "\">" + \
				    name + "</a></label>" + rest
				i = i + 1
				continue
		lines[i] = line
		i = i + 1
	return "\n".join(lines)

def request_rescan(technology_type):
	path = "/net/connman/technology/" + technology_type
	bus = dbus.SystemBus()
	try:
		technology = dbus.Interface(bus.get_object("net.connman", path),
					    "net.connman.Technology")
		technology.Scan()
	except:
		return

def is_known_service(service_id):
	properties = get_properties(service_id)
	if len(properties) == 0:
		return False
	favorite = get_raw_value(properties, "Favorite")
	if favorite == None:
		return False
	else:
		return favorite

def is_vpn_service(service_id):
	properties = get_properties(service_id)
	if len(properties) == 0:
		return False
	return get_value(properties, "Type") == "vpn"

def is_immutable_service(service_id):
	properties = get_properties(service_id)
	if len(properties) == 0:
		return False
	return get_value(properties, "Immutable") == "true"

def get_security(service_id):
	properties = get_properties(service_id)
	if len(properties) == 0:
		return []
	return get_value(properties, "Security")

def get_bt_devices():
	return []
