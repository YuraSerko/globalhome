var cboxes = 0

$(document).ready(function() {
	UpdateCBoxes()
	UpdateLink()
})

function UpdateCBoxes() {
	cboxes = $("ul > li > label > input:checkbox")
	for (var i = 0; i < cboxes.length; i++)
		$(cboxes[i]).change(UpdateLink)
}

function UpdateLink() {
	UpdateCBoxes()
    var id_str = "?ids="
    
    for (var i = 0; i < cboxes.length; i++)
        if (cboxes[i].checked)
            id_str += cboxes[i].value + ","
    
    var a_str = " \
    window.open('/content_variables/show_many/" + id_str + "', '', \
    'width=750,height=500,status=no,location=no,toolbar=no,menubar=no,scrollbars=1'); return false;"
    $("#show_all_vars_link").attr("onClick", a_str)
}
