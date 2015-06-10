   function text (str) { return /[0-9_;:'!~?=+<|>]/g.test(str); }

   function numeric (str) { return /^[0-9-\+\(\)\s]+z/.test(str + "z"); }

   function mail (str) { return /^[a-z0-9_\.]+@[a-z0-9_\.]+.[a-z]{2,3}$/.test(str); }
   
   function checkForm (index) 
      {
      var title;
      var elem;
      var dutyField = "Не заполнено поле ";
      var wrongField = "Неверное значение поля ";
      var check = true;
      function checkError (field, str) 
         {
         document.getElementById('alert'+index).innerHTML = str;
		 document.getElementById('alert_tr').style.display = 'table-row';
         check = false;
         }

    	  document.getElementById('alert'+index).innerHTML = "";
		  document.getElementById('alert_tr').style.display = 'none';

     if (check)
         {
         title = '"Фамилия"';
		 
         elem = document.getElementById('surname'+index).value;
         if (elem.length == 0) 
		 {
         document.getElementById('surname'+index).focus();
		 checkError('surname'+index, dutyField + title);
		 }
         else if (text(elem)) checkError('surname'+index, wrongField + title);
         }
		 
      if (check)
         {
         title = '"Имя"';
         elem = document.getElementById('name'+index).value;
         if (elem.length == 0) 
		 {
         document.getElementById("name"+index).focus();
		 checkError('name'+index, dutyField + title);
		 }
         else if (text(elem)) checkError('name'+index, wrongField + title);
         }
		 
      if (check)
         {
         title = '"Отчество"';
         elem = document.getElementById('patronymic'+index).value;
         if (elem.length == 0) 		 
		 {
         document.getElementById("patronymic"+index).focus();
		 checkError('patronymic'+index, dutyField + title);
		 }
         else if (text(elem)) checkError('patronymic'+index, wrongField + title);
         }
	     
      if (check)
         {
         title = '"Почтовой ящик (email)"';
         elem = document.getElementById('email'+index).value;
         if (elem.length == 0) 
		 {
         document.getElementById("email"+index).focus();
		 checkError('email'+index, dutyField + title);
		 }
         else if (!mail(elem)) checkError('email'+index, wrongField + title);
         }

      if (check)
         {
         title = '"Номер телефона"';
         elem = document.getElementById('phoneNumber'+index).value;
         if (elem.length == 0)
		 {
         document.getElementById("phoneNumber"+index).focus();
		 checkError('phoneNumber'+index, dutyField + title);
		 }
         else if (!numeric(elem)) checkError('phoneNumber'+index, wrongField + title);
         }
		 
     if (check)  { document.getElementById('preview'+index).submit(); }
	 
      return check;
      }
	  
function ochistka(index) 
 {
if (index == 'rack')
	{
	document.getElementById('alert').innerHTML = "";
	document.getElementById('alert_tr').style.display = 'none';
	}
else
	{
	document.getElementById("cost").innerHTML="2100";
	document.getElementById('alert').innerHTML = "";
	document.getElementById('alert_tr').style.display = 'none';
	}
 }
	  