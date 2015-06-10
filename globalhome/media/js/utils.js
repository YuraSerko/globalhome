
function PopupWindow(link) {
	var win = window.open(link.href + "?_popup=1", "", 'height=500,width=800,resizable=yes,scrollbars=yes');
	win.focus();
	return false
}
