
function show_hide_proxy_fields(mySel) {
    if (typeof mySel == 'object')
	value = mySel.value;
    else
	value = mySel
    switch (value) {
    case 'auto':
	document.getElementById('proxy-url').style.display = 'inline';
	document.getElementById('proxy-servers').style.display = 'none';
	document.getElementById('proxy-excludes').style.display = 'none';
	break;
    case 'manual':
	document.getElementById('proxy-url').style.display = 'none';
	document.getElementById('proxy-servers').style.display = 'inline';
	document.getElementById('proxy-excludes').style.display = 'inline';
	break;
    case 'direct':
	document.getElementById('proxy-url').style.display = 'none';
	document.getElementById('proxy-servers').style.display = 'none';
	document.getElementById('proxy-excludes').style.display = 'none';
	break;
    }
}


function show_hide_ipv4_fields(mySel) {
    if (typeof mySel == 'object')
	value = mySel.value;
    else
	value = mySel
    switch (value) {
    case 'dhcp':
    case 'off':
	document.getElementById('ipv4address').style.display = 'none';
	document.getElementById('ipv4netmask').style.display = 'none';
	document.getElementById('ipv4gateway').style.display = 'none';
	break;
    case 'fixed':
	document.getElementById('ipv4address-id').style.display = 'none';
	document.getElementById('ipv4netmask-id').style.display = 'none';
	document.getElementById('ipv4gateway-id').style.display = 'none';
	document.getElementById('ipv4method').disabled = true;
	break;
    case 'manual':
	document.getElementById('ipv4address').style.display = 'inline';
	document.getElementById('ipv4netmask').style.display = 'inline';
	document.getElementById('ipv4gateway').style.display = 'inline';
	break;
    }
}


function show_hide_ipv6_fields(mySel) {
    if (typeof mySel == 'object')
	value = mySel.value;
    else
	value = mySel
    switch (value) {
    case 'auto':
    case 'off':
	document.getElementById('ipv6address').style.display = 'none';
	document.getElementById('ipv6prefixlen').style.display = 'none';
	document.getElementById('ipv6gateway').style.display = 'none';
	break;
    case 'fixed':
	document.getElementById('ipv6address-id').style.display = 'none';
	document.getElementById('ipv6prefixlen-id').style.display = 'none';
	document.getElementById('ipv6gateway-id').style.display = 'none';
	document.getElementById('ipv6method').disabled = true;
	break;
    case 'manual':
	document.getElementById('ipv6address').style.display = 'inline';
	document.getElementById('ipv6prefixlen').style.display = 'inline';
	document.getElementById('ipv6gateway').style.display = 'inline';
	break;
    }
}


function helpPopup(url) {
    popupWindow = window.open(
	url,
	'popUpWindow',
	'height=800,width=600,left=10,top=10,resizable=yes,scrollbars=yes,'+
	    'toolbar=yes,menubar=no,location=no,directories=no,status=yes'
    )
}
