from string import translate,maketrans,punctuation
import web
from web import form
import config
import dbus
from util import get_properties, get_raw_value, get_value, get_str_value, \
    get_dict_value, get_service, get_security

vssid = form.regexp(r".{1,32}$", "Must be between 1 and 32 characters")
vprefix = form.Validator('Must be between 0 and 128',
                          lambda x: x=="" or int(x)>=0 and int(x)<=128)
vallowempty = form.Validator('', lambda x: x=="")
vpin = form.regexp(r".{4,8}$", "Must be between 4 and 8 characters")

form = web.form.Form(
    form.Hidden('servicetype'),
    form.Radio('autoconnect', args=["Yes", "No"], description="Autoconnect"),
    form.Textbox("domains", class_="textEntry", size=64, description="Domains"),
    form.Textbox("timeservers", class_="textEntry", size=64,
                 description="Timeservers"),
    form.Textbox("nameservers", class_="textEntry", size=64,
                 description="Nameservers"),
    form.Dropdown("ipv4method",
                  [('fixed','Fixed'),('dhcp','DHCP'),('manual','Manual'),
                   ('off','Off')],
                  onChange="show_hide_ipv4_fields(this);",
                  description="IPv4 configuration"),
    form.Textbox("ipv4address", size=15, description="IPv4 address"),
    form.Textbox("ipv4netmask", size=15, description="IPv4 netmask"),
    form.Textbox("ipv4gateway", size=15, description="IPv4 gateway"),
    form.Dropdown("ipv6method",
                  [('fixed','Fixed'),('auto','Automatic'),('manual','Manual'),
                   ('off','Off')],
                  onChange="show_hide_ipv6_fields(this);",
                  description="IPv6 configuration"),
    form.Textbox("ipv6address", size=46, description="IPv6 address"),
    form.Textbox("ipv6prefixlen", vprefix, size=4,
                 description="IPv6 prefix length"),
    form.Textbox("ipv6gateway", size=46, description="IPv6 gateway"),
    form.Dropdown("ipv6privacy",
                  [('disabled','Disabled'),('enabled','Enabled'),
                   ('prefered','Prefered')],
                  description="IPv6 privacy"),
    form.Dropdown("proxymethod",
                  [('auto','Automatic'),('manual','Manual'),
                   ('direct','Direct')],
                  onChange="show_hide_proxy_fields(this);",
                  description='Proxy method'),
    form.Textbox("proxyurl", size=64, description="Proxy URL",
                 class_="textEntry", id="proxy-url"),
    form.Textbox("proxyservers", size=64, description="Proxy server URIs",
                 class_="textEntry", id="proxy-servers"),
    form.Textbox("proxyexcludes", size=64, description="Proxy host excluded",
                 class_="textEntry", id="proxy-excludes"),

    form.Button("Submit", type="submit", value="edit", html="Save"),
    form.Button("Submit", type="submit", value="connect", html="Connect"),
    form.Button("Submit", type="submit", value="disconnect", html="Disconnect"),
    form.Button("Submit", type="submit", value="remove", html="Remove")
)

def update_fields(service_id):
    properties = get_properties(service_id)
    if not properties.keys():
        return

    if get_value(properties, "AutoConnect") == "true":
        autoconn = "Yes"
    else:
        autoconn = "No"
    form.get('autoconnect').value = autoconn

    form.get('nameservers').value = get_str_value(properties,
                                                  "Nameservers.Configuration")
    form.get('timeservers').value = get_str_value(properties,
                                                  "Timeservers.Configuration")
    form.get('domains').value = get_str_value(properties,
                                              "Domains.Configuration")
    value = get_dict_value(properties, "Proxy.Configuration", "Method")
    if value == "":
        value = "auto"
    form.get('proxymethod').value = value
    form.get('proxyurl').value = get_dict_value(properties,
                                                "Proxy.Configuration", "URL")
    form.get('proxyservers').value = get_dict_value(properties,
                                                    "Proxy.Configuration",
                                                    "Servers")
    form.get('proxyexcludes').value = get_dict_value(properties,
                                                     "Proxy.Configuration",
                                                     "Excludes")
    form.get('ipv4method').value = get_dict_value(properties,
                                                   "IPv4.Configuration",
                                                   "Method")
    form.get('ipv4address').value = get_dict_value(properties,
                                                   "IPv4.Configuration",
                                                   "Address")
    form.get('ipv4netmask').value = get_dict_value(properties,
                                                   "IPv4.Configuration",
                                                   "Netmask")
    form.get('ipv4gateway').value = get_dict_value(properties,
                                                   "IPv4.Configuration",
                                                   "Gateway")
    form.get('ipv6method').value = get_dict_value(properties,
                                                   "IPv6.Configuration",
                                                   "Method")
    form.get('ipv6address').value = get_dict_value(properties,
                                                   "IPv6.Configuration",
                                                   "Address")
    value = get_dict_value(properties, "IPv6.Configuration",
                           "PrefixLength")
    if value != "":
        value = "%d" % value
    form.get('ipv6prefixlen').value = value
    form.get('ipv6gateway').value = get_dict_value(properties,
                                                   "IPv6.Configuration",
                                                   "Gateway")
    form.get('ipv6privacy').value = get_dict_value(properties,
                                                   "IPv6.Configuration",
                                                   "Privacy")


def changed(properties, value, input):
    if get_value(properties, value) != input:
        return True
    else:
        return False

def change(service, properties, value, input, type = None):
    if changed(properties, value, input):
        if type != None:
            try:
                service.SetProperty(value, type)
            except dbus.DBusException, error:
                print "type %s error when setting %s" % (type, value)
                return (False, error)
        else:
            try:
                service.SetProperty(value, input)
            except dbus.DBusException, error:
                print "input %s error when setting %s" % (input, value)
                return (False, error)
    return (True, None)

def make_variant(string):
	return dbus.String(string, variant_level=1)

def make_byte_variant(string):
    return dbus.Byte(int(string), variant_level=1)

def changed_dict(properties, block, key, input):
    if get_dict_value(properties, block, key) != input:
        print "%s.%s = %s != %s" % (block, key,
                                    get_dict_value(properties, block, key),
                                    input)
        return True
    else:
        return False

def changed_dict_byte(properties, block, key, input):
    value = "%d" % get_dict_value(properties, block, key)
    if value != input:
        return True
    else:
        return False

def service_not_found(service_id, error = None, extra = None):
    if error != None:
        if error._dbus_error_name == "net.connman.Error.InvalidArguments":
            if extra != None:
                return "Invalid argument given when trying to edit %s service %s" % (extra, service_id)
            else:
                return "Invalid argument given when trying to edit service %s" % service_id
        else:
            if extra != None:
                return "service %s: %s: %s" % (service_id, error._dbus_error_name, extra)
            else:
                return "Service %s: %s" % (service_id, error._dbus_error_name)
    if extra != None:
        return "Service %s: %s" % (service_id, extra)
    else:
        return "Service %s is not found. It was probably expired, please rescan and try again." % service_id

def split_string(S):
    # strip " ," from input string and split it into list
    chars_to_strip = " ,"
    T = maketrans(chars_to_strip, ' '*len(chars_to_strip))
    return translate(S, T).split()

def update_service(input, service_id):
    properties = get_properties(service_id)
    if not properties.keys():
        return "No properties for service %s" % service_id

    service = get_service(service_id)

    try:
        if input.autoconnect == "Yes":
            autoconnect = True
        else:
            autoconnect = False
        (value_changed, error) = change(service, properties, "AutoConnect",
                                        autoconnect)
        if not value_changed:
            return service_not_found(service_id, error, "AutoConnect")
    except:
        pass

    try:
        (value_changed, error) = change(service, properties,
                                        "Domains.Configuration",
                                        input.domains,
                                        dbus.Array([input.domains],
                                                signature=dbus.Signature('s')))
        if not value_changed:
            return service_not_found(service_id, error, "Domains")
    except:
        pass

    try:
        (value_changed, error) = change(service, properties,
                                        "Nameservers.Configuration",
                                        input.nameservers,
                                        dbus.Array([input.nameservers],
                                               signature=dbus.Signature('s')))
        if not value_changed:
            return service_not_found(service_id, error, "Nameservers")
    except:
        pass

    try:
        (value_changed, error) = change(service, properties,
                                        "Timeservers.Configuration",
                                        input.timeservers,
                                        dbus.Array([input.timeservers],
                                               signature=dbus.Signature('s')))
        if not value_changed:
            return service_not_found(service_id, error, "Timeservers")
    except:
        pass

    try:
        if input.proxymethod == "auto":
            if changed_dict(properties, "Proxy.Configuration", "URL",
                            input.proxyurl):
                proxy = { "Method": make_variant("auto") }
                proxy["URL"] = make_variant(input.proxyurl)
                try:
                    service.SetProperty("Proxy.Configuration", proxy)
                except dbus.DBusException, error:
                    return service_not_found(service_id, error,
                                             "Proxy URL setting failed")

        elif input.proxymethod == "manual":
            set_property = False
            proxy = { "Method": make_variant("manual") }
            if changed_dict(properties, "Proxy.Configuration", "Servers",
                            input.proxyservers):
                proxy["Servers"] = split_string(input.proxyservers)
                set_property = True

            if changed_dict(properties, "Proxy.Configuration", "Excludes",
                        input.proxyexcludes):
                proxy["Excludes"] = split_string(input.proxyexcludes)
                set_property = True

            if set_property:
                try:
                    service.SetProperty("Proxy.Configuration",
                                        dbus.Dictionary(proxy, signature='sv'))
                except dbus.DBusException, error:
                    return service_not_found(service_id, error,
                                             "Manual Proxy setting failed")
    except:
        pass

    try:
        ipv4method = input.ipv4method
    except:
        ipv4method = "fixed"

    if ipv4method == "manual":
        set_property = False
        ipv4 = { "Method": make_variant("manual") }
        if changed_dict(properties, "IPv4.Configuration", "Method",
                        ipv4method):
            set_property = True
        if changed_dict(properties, "IPv4.Configuration", "Address",
                        input.ipv4address):
            ipv4["Address"] = make_variant(input.ipv4address)
            set_property = True
        if changed_dict(properties, "IPv4.Configuration", "Netmask",
                        input.ipv4netmask):
            ipv4["Netmask"] = make_variant(input.ipv4netmask)
            set_property = True
        if changed_dict(properties, "IPv4.Configuration", "Gateway",
                        input.ipv4gateway):
            ipv4["Gateway"] = make_variant(input.ipv4gateway)
            set_property = True

        if set_property:
            try:
                service.SetProperty("IPv4.Configuration",
                                    dbus.Dictionary(ipv4, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv4 manual setting failed")

    elif ipv4method == "dhcp":
        if changed_dict(properties, "IPv4.Configuration", "Method",
                        ipv4method):
            ipv4 = { "Method": make_variant("dhcp") }

            try:
                service.SetProperty("IPv4.Configuration",
                                    dbus.Dictionary(ipv4, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv4 dhcp setting failed")

    elif ipv4method == "off":
        if changed_dict(properties, "IPv4.Configuration", "Method",
                        ipv4method):
            ipv4 = { "Method": make_variant("off") }

            try:
                service.SetProperty("IPv4.Configuration",
                                    dbus.Dictionary(ipv4, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv4 dhcp setting failed")

    try:
        ipv6method = input.ipv6method
    except:
        ipv6method = "fixed"

    if ipv6method == "manual":
        set_property = False
        ipv6 = { "Method": make_variant("manual") }
        if changed_dict(properties, "IPv6.Configuration", "Method",
                        ipv6method):
            set_property = True
        if changed_dict(properties, "IPv6.Configuration", "Address",
                        input.ipv6address):
            ipv6["Address"] = make_variant(input.ipv6address)
            set_property = True
        if changed_dict_byte(properties, "IPv6.Configuration", "PrefixLength",
                        input.ipv6prefixlen):
            ipv6["PrefixLength"] = make_byte_variant(input.ipv6prefixlen)
            set_property = True
        if changed_dict(properties, "IPv6.Configuration", "Gateway",
                        input.ipv6gateway):
            ipv6["Gateway"] = make_variant(input.ipv6gateway)
            set_property = True

        if set_property:
            try:
                service.SetProperty("IPv6.Configuration",
                                    dbus.Dictionary(ipv6, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv6 manual setting failed")

    elif ipv6method == "auto":
        set_property = False
        ipv6 = { "Method": make_variant("auto") }
        if changed_dict(properties, "IPv6.Configuration", "Method",
                        ipv6method):
            set_property = True

        if changed_dict(properties, "IPv6.Configuration", "Privacy",
                        input.ipv6privacy):
            ipv6["Privacy"] = make_variant(input.ipv6gateway)
            set_property = True

        if set_property:
            try:
                service.SetProperty("IPv6.Configuration",
                                    dbus.Dictionary(ipv6, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv6 auto setting failed")

    elif ipv6method == "off":
        if changed_dict(properties, "IPv6.Configuration", "Method",
                        ipv6method):
            ipv6 = { "Method": make_variant("off") }

            try:
                service.SetProperty("IPv6.Configuration",
                                    dbus.Dictionary(ipv6, signature='sv'))
            except dbus.DBusException, error:
                return service_not_found(service_id, error,
                                         "IPv6 off setting failed")

    return None

def remove_service(input, service_id):
    service = get_service(service_id)
    try:
        service.Remove()
    except:
        return "Invalid or missing service %s" % service_id

    return None
