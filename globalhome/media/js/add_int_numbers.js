function displayAll()
{
	var x=document.getElementById("selected_numbers2")
		
}

function displayResult()
{
var x=document.getElementById("selected_numbers2");
var option=document.createElement("option");


option.text=document.getElementById("selected_numbers").options[document.getElementById("selected_numbers").selectedIndex].text
var a = document.getElementById('selected_numbers2');
var k=0
try
  { 

      x.add(option,x.options[null]);
   }
catch (e)
  {
 x.add(option,x.options[null]);}
  
var x = document.getElementById('selected_numbers');
   for (i = x.length - 1; i>=0; i--) {
      if (x.options[i].selected) {
		
		
        x.remove(i);
		
      }
   }
refr();
}


function displayResult2()
{
var x=document.getElementById("selected_numbers");
var option=document.createElement("option");


option.text=document.getElementById("selected_numbers2").options[document.getElementById("selected_numbers2").selectedIndex].text
var a = document.getElementById('selected_numbers0');
var k=0
try
  { 

      x.add(option,x.options[null]);
   }
catch (e)
  {
 x.add(option,x.options[null]);}

var x = document.getElementById('selected_numbers2');
   for (i = x.length - 1; i>=0; i--) {
      if (x.options[i].selected) {
        x.remove(i);
      }
   }
   refr();
}


function refr()
{
var x = document.getElementById("selected_numbers2");
document.getElementById("int_numb").value="";
   for (i = x.length - 1; i>=0; i--) {
	document.getElementById("int_numb").value=document.getElementById("int_numb").value+document.getElementById("selected_numbers2").options[i].text.split(" ")[0]+",";   
	
   }
}

function displayResult3()
{
var sel_1=document.getElementById("selected_numbers");
var sel_2=document.getElementById("selected_numbers2");
while(sel_1.options.length>0) sel_2.appendChild(sel_1.options[0]);
refr();
}

function displayResult4()
{
var sel_1=document.getElementById("selected_numbers2");
var sel_2=document.getElementById("selected_numbers");
while(sel_1.options.length>0) sel_2.appendChild(sel_1.options[0]);
refr();
}