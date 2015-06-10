
function Reflect(obj) {
    var s = ""
    for (var i in obj)
        s += "> " + i + ": " + obj[i] + "\n"
    return s 
}

function AddFutureGroupData(data) {
    window.future_data = data
}

function GroupAddSuccess(new_id) {
    window.future_data["id"] = new_id
    window.groups.push(window.future_data)
    SetItems(window.groups, new_id)
}

function AddGroup() {
	href = '/account/phones_groups/add/?popup_window=1'
	if (window.extra_addgroup_get_query !== undefined)
		href += "&" + window.extra_addgroup_get_query
    window.add_window = window.open(
        href, '', 
        'width=850,height=400,status=no,location=no,toolbar=no,menubar=no,scrollbars=1'
    )
}

function SetItems(items, initial_id) {
    window.ignore_on_change = true
    window.group_select.empty()
    var s = ""
    for (var i = 0; i < items.length; i++) {
        s += '<option value="' + items[i].id + '" '
        if (items[i].id == initial_id) {
            s += 'selected= true'
            var selected = i
        }
        s += ">" + items[i].name + "</option>\n"
    
    }
    
    window.group_select.append(s)
    window.group_select.attr("selected", selected)
    window.ignore_on_change = false
    ShowNumbersInSelectedGroup()
}

function Setup() {
    window.div_numbers = $("#numbers-of-selected-group")
    window.group_select = $("#id_user_groups")
    window.group_select.attr("onChange", "ShowNumbersInSelectedGroup()")
    window.add_group_button = $("#add-group-button")
    window.add_group_button.attr("onClick", "AddGroup(); return false;")
    window.ignore_on_change = false
    window.groups = window.widget_initial_choices
    SetItems(window.groups, window.selected_id)
}

function ShowNumbersInSelectedGroup() {
    var value = window.group_select.attr("value")
    for (var i = 0; i < window.groups.length; i++)
        if (window.groups[i].id == value) {
            window.div_numbers.empty()
            s = "<ul>"
            for (var j = 0; j < window.groups[i].numbers.length; j++)
                s += "<li>" + window.groups[i].numbers[j] + "</li>"
            s += "</ul>"
            window.div_numbers.append(s)
        }
}









