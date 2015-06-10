function GetI(id)
{
  return document.getElementById(id);
}
function IsDivIdVisible(div_id)
{
  if (GetI(div_id).style.display == 'none')
    return false;
  else
    return true;
}
function SetDivIdVisible(div_id, value)
{
  if (value)
    GetI(div_id).style.display = 'block';
  else
    GetI(div_id).style.display = 'none';
}
function ToggleDivIdVisible(div_id)
{
  var visible = IsDivIdVisible(div_id);
  SetDivIdVisible(div_id, !visible);
}
function IsDivVisible(div)
{
  return div.style.display != 'none';
}
function SetDivVisible(div, value)
{	
  if (value)
    div.style.display = 'block';
  else
    div.style.display = 'none';
}
function Sdown(div, a)
{	
  if (a.checked)
    div.style.display = 'block';
  else
    div.style.display = 'none';
}
function ToggleDivVisible(div)
{
  var visible = IsDivVisible(div);
  SetDivVisible(div, !visible);
}
function OpenInSmallWindow(url)
{
    var wnd = window.open(url, "", "left=10,top=10,width=970,height=615");
    return false;
}
function ShowAllIds()
{
    var items = document.getElementsByTagName('*');
    var s = "";
    for(var i=0; i < items.length; i++)
        if (items[i].id != "")
          s += items[i].id + "\n";
    alert(s);
}
