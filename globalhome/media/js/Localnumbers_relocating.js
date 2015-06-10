
function FilterLocalnumbersByRegion() {
    var ncb = $("ul > li > label > input:checkbox")
    var region_tds = $("#region-numbers > td")
    var expr = /reg_(\d+)\w*/
    for (var i = 0; i < ncb.length; i++) {
        var region = expr.exec(ncb[i].value)[1]
        $(region_tds[region - 1]).append($(ncb[i]).parent().parent())
    }
    $("#numbers-cb-default").empty()

}
