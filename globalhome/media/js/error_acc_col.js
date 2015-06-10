// JavaScript Document   
   
function checkForm () 
  {
  var title;
  var elem;
  var dutyField = "Не заполнено поле ";
  var check = true;
  function checkError (field, str) 
  
	 {
	 document.getElementById('alert').innerHTML = str;
	 document.getElementById('alert_tr').style.display = 'table-row';
	 check = false;
	 }
	 document.getElementById('alert').innerHTML = "";
	 document.getElementById('alert_tr').style.display = 'none';
	
 if (check)
	 {
	 title = '"Название оборудования"';
	 
	 elem = document.getElementById('equipment').value;
	 if (elem.length == 0) 
	 {
	 document.getElementById('equipment').focus();
	 checkError('equipment', dutyField + title);
	 }
	 
	 
 if (check)  { document.getElementById('preview').submit(); }
 
  return check;
  }
  }
	  
function ochistka () 
 {
  document.getElementById('alert').innerHTML = "";
  document.getElementById('alert_tr').style.display = 'none';
 } 