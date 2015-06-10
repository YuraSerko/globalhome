// JavaScript Document
function cost_unit(a)
{
document.getElementById("hidden_unit").value=a.value;
document.getElementById("hidden_cost").value=a.value*500+(document.getElementById("hidden_port").value-1)*500+(document.getElementById("hidden_dop_IP").value-1)*80+(document.getElementById("hidden_rozetka").value-1)*400+(document.getElementById("hidden_electro").value-400)*4.5+1600 ;
document.getElementById("cost").innerHTML=document.getElementById("hidden_cost").value;
}
function cost_port(a)
{
document.getElementById("hidden_port").value=a.value;
document.getElementById("hidden_cost").value=(a.value-1)*500+(document.getElementById("hidden_unit").value)*500+(document.getElementById("hidden_dop_IP").value-1)*80+(document.getElementById("hidden_rozetka").value-1)*400+(document.getElementById("hidden_electro").value-400)*4.5+1600 ;
document.getElementById("cost").innerHTML=document.getElementById("hidden_cost").value;
}
function cost_dop_IP(a)
{
document.getElementById("hidden_dop_IP").value=a.value;
document.getElementById("hidden_cost").value=(a.value-1)*80+(document.getElementById("hidden_port").value-1)*500+document.getElementById("hidden_unit").value*500+(document.getElementById("hidden_rozetka").value-1)*400+(document.getElementById("hidden_electro").value-400)*4.5+1600 ;
document.getElementById("cost").innerHTML=document.getElementById("hidden_cost").value;
}
function cost_rozetka(a)
{
document.getElementById("hidden_rozetka").value=a.value;
document.getElementById("hidden_cost").value=(a.value-1)*400+(document.getElementById("hidden_port").value-1)*500+(document.getElementById("hidden_dop_IP").value-1)*80+document.getElementById("hidden_unit").value*500+(document.getElementById("hidden_electro").value-400)*4.5+1600 ;
document.getElementById("cost").innerHTML=document.getElementById("hidden_cost").value;
}
function cost_electro(a)
{
document.getElementById("hidden_electro").value=a.value;
document.getElementById("hidden_cost").value=(a.value-400)*4.5+(document.getElementById("hidden_port").value-1)*500+(document.getElementById("hidden_dop_IP").value-1)*80+(document.getElementById("hidden_rozetka").value-1)*400+document.getElementById("hidden_unit").value*500+1600 ;
document.getElementById("cost").innerHTML=document.getElementById("hidden_cost").value;
}