// JavaScript Document
function pc_vds(a)
{
document.getElementById("hidden_hand").value=a.value;
document.getElementById("os_hand").innerHTML = document.getElementById("hidden_hand").value
}
function pc256(a)
{
document.getElementById("hidden_os256").value=a.value;
document.getElementById("os256").innerHTML = document.getElementById("hidden_os256").value
}
function pc512(a)
{
document.getElementById("hidden_os512").value=a.value;
document.getElementById("os512").innerHTML = document.getElementById("hidden_os512").value	
}
function pc1024(a)
{
document.getElementById("hidden_os1024").value=a.value;
document.getElementById("os1024").innerHTML = document.getElementById("hidden_os1024").value
}
function pc2048(a)
{
document.getElementById("hidden_os2048").value=a.value;
document.getElementById("os2048").innerHTML = document.getElementById("hidden_os2048").value
}
function pc3072(a)
{
document.getElementById("hidden_os3072").value=a.value;
document.getElementById("os3072").innerHTML = document.getElementById("hidden_os3072").value
}
function form_show()
{
document.getElementById("slider_cpu").style.visibility="visible";
document.getElementById("slider_ram").style.visibility="visible";
document.getElementById("slider_hdd").style.visibility="visible";
document.getElementById("slider_ip").style.visibility="visible";
}
function form_hide()
{
document.getElementById("slider_cpu").style.visibility="hidden"
document.getElementById("slider_ram").style.visibility="hidden"
document.getElementById("slider_hdd").style.visibility="hidden"
document.getElementById("slider_ip").style.visibility="hidden"
}

function form_hide_vds()
{
document.getElementById("slider_cpu").style.visibility="hidden"
document.getElementById("slider_ram").style.visibility="hidden"
document.getElementById("slider_hdd").style.visibility="hidden"
document.getElementById("slider_ip").style.visibility="hidden"
document.getElementById("hidden_hand_cpu").value = document.getElementById("hidden_cpu").value
document.getElementById("cpu").innerHTML = document.getElementById("hidden_hand_cpu").value
document.getElementById("hidden_hand_ram").value = document.getElementById("hidden_ram").value
document.getElementById("ram").innerHTML = document.getElementById("hidden_hand_ram").value
document.getElementById("hidden_hand_hdd").value = document.getElementById("hidden_hdd").value
document.getElementById("hdd").innerHTML = document.getElementById("hidden_hand_hdd").value
document.getElementById("hidden_hand_ip").value = document.getElementById("hidden_ip").value
document.getElementById("ip").innerHTML = document.getElementById("hidden_hand_ip").value
document.getElementById("cost_hand").innerHTML = document.getElementById("hidden_cost").value
}
