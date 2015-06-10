var items=1;
var total_cost=0;
var do_continue = true;

////////////////////////////////////////////////////////////////////////////////////
// по нажатию на кнопку заказать (под типом оборудования) делаем запрос к базе данных по данному виду оборудования + список всех видов
function step_zakaz(id)
{   
		$.ajax({
				url: "/equipment_rent/step_zakaz/False/"+id+"/",
                cache: false,
				async: false,
                success: function(html){
                   $("#id_popup").html(html);
                   
					  
                }  
            });
}

 	
 function chek_step_auth(){
 		 //проверка полей на введенные значения. (количество на цифру), если есть доставка то телефон (на цифру), адрес -наличие
 		 var once_done = false;
 		 var do_continue = true;
	     for (i=1; i<=items; i++)
	 	  {     
	    	    //количество
		        var quan_temp_id = 'quantity/' + i;
		        var quan_temp_elem = document.getElementById(quan_temp_id);
				if (quan_temp_elem) { //если не был удален 
					if ((!numeric(document.getElementById(quan_temp_id).value)) &&(!once_done))
						 {
						  document.getElementById(quan_temp_id).focus();
						  document.getElementById('error').innerHTML = 'Введите цифру'
						  document.getElementById('error').style.display='table-cell';
						  once_done = true;
						  do_continue = false;
						  }
		        }
	      }
		   // доставка
		   var select_delivery = document.getElementById('delivery'); // получаем список всех элементов (количество)
		   //var selected_delivery = select_delivery.options[select_delivery.selectedIndex].value; // получаем значение выделенного элемента (количество)
            var selected_delivery = select_delivery.value
		   if (selected_delivery=='delivery')
			   {
			    del_elem = document.getElementById('delivery_address').value 
			    tel_elem = document.getElementById('tel_number').value 
			    if ((del_elem == 0)&&(!once_done))
			             {
			    	      document.getElementById('delivery_address').focus();
			    	      document.getElementById('error').innerHTML = 'Введите адрес доставки';
						  document.getElementById('error').style.display='table-cell';
						  once_done = true;
						  do_continue = false;
						  }
			    if ((tel_elem == 0)&&(!once_done))
	                     {document.getElementById('tel_number').focus();
			    	      document.getElementById('error').innerHTML = 'Введите номер телефона';
				          document.getElementById('error').style.display='table-cell';
				          once_done = true;
				          do_continue = false;
				          }
			    if (  (tel_elem != 0)  &&  (!numeric(tel_elem))  &&  (!once_done)  )
			    	     {
			    	      document.getElementById('tel_number').focus();
					      document.getElementById('error').innerHTML = 'Введите цифру'
					      document.getElementById('error').style.display='table-cell';
					      once_done = true;
					      do_continue = false;
					      }
			   }
    return do_continue;
 }
////////////////////////////////////////////////////////////////////////////////////
function step_auth(device_id, account)
{	do_continue  = chek_step_auth();
	if (do_continue) {
		var spis_equipment = ""; 
		for (var i=1; i<=items; i++)
		    {
			var idd = "device_type/" + i;
			var idq = "quantity/" + i;
			if  (document.getElementById(idd))
			    {
				spis_equipment = spis_equipment + document.getElementById(idd).value + ":";
				spis_equipment = spis_equipment + document.getElementById(idq).value + ",";
			    }
			}
		get = "&equipments=" + spis_equipment;
		var select_delivery = document.getElementById('delivery'); // получаем список всех элементов (доставка)
		//var selected_delivery = select_delivery.options[select_delivery.selectedIndex].value; // получаем значение выделенного элемента (доставка)
	    var selected_delivery = select_delivery.value
        if (selected_delivery=='delivery'){
	    	get += "&delivery_address=" + document.getElementById("delivery_address").value;
			get += "&tel_number=" + document.getElementById("tel_number").value;
	        }
		var str = $("#equipment_rent_zakaz").serialize();
		$.ajax({
		url: '/equipment_rent/step_auth/'+ account +'/?'+str+get,
		cache: false,
		async: false,
		  
		success: function(html){
			$("#id_popup").html(html);
            console.log('/equipment_rent/step_auth/'+ account +'/?'+str+get)

		}  
		});
		
	}
 }
/////////////////////////////////////////////////////////////////////////////////////
//работает по нажатию кнопки далее после submit формы в регистрации или логировании
     	function step_final(req)
	{	
		var str = $("#form_auth").serialize();
		$.ajax({
                url: "/equipment_rent/step_"+req+"/?"+str,
                cache: false,
				async: false,				  
                success: function(html){				
                    $("#id_popup").html(html);	  
                },
                error: function(data){
                    console.log(data.responseText)

                }
            });
     }


//////////////////////////////////////////////////////////////////////////////////////////
//по выбору в элементе select "доставка/нет доставки" отображает/показывает скрытые поля
	function need_of_delivery(val)
    {
     	 if (val == 'delivery')
     	      {
     		   document.getElementById('take_away_address').style.display = 'none';
     	       document.getElementById('ad_dil_label').style.display='table-cell';
     	       document.getElementById('ad_dil_input').style.display='inline-table';
     	       document.getElementById('ad_tel_label').style.display='table-cell';
    	       document.getElementById('ad_tel_input').style.display='table-cell';
    	       
    	      //проверка на введеный символ в поле tel_number
    	      input=document.getElementById('tel_number');
    	 	  input.oninput = function fun() {
    	 	  id = document.activeElement.id;
    	 	  value = document.activeElement.value;
    	 	  //добавим проверку введенных данных (поле количество)
    	 	  if (!numeric(value))  {
    	 			document.getElementById('error').innerHTML = 'Введите цифру'
    	 			document.getElementById('error').style.display='table-cell';
    	 			  }
    	 	  else  {
    	 				document.getElementById('error').style.display='none';
    	 			  }
    	 	    }
    	      }
     	 if (val == 'no_delivery')
     	      {
     		   document.getElementById('take_away_address').style.display = 'table-cell';
     	       document.getElementById('ad_dil_label').style.display='none';
     	       document.getElementById('ad_dil_input').style.display='none';
     	       document.getElementById('ad_tel_label').style.display='none';
    	       document.getElementById('ad_tel_input').style.display='none';}

    	  $('#my').css("height", "auto");
		  var h = $('#id_popup').height();
		  var h1 = $(window).height();
		  var stpx = h1.toString() + "px";
		  if (h1-h<0)
			  {  
			  	  $('#my').css("overflow-y", "scroll");
			  	  $('#my').css("height", stpx);}                                        
		  
		  if (h1-h>0)
		  {  
			  $('#my').css("overflow-y", "hidden");
		  	  $('#my').css("height", "auto");}    
    	  
	}


//////////////////////////////////////////////////////////////////////////////////////////
//на изменение выбранного типа оборудования select "device_id" или количества  select "quantity" меняем его (абонетскую плату и стоимость или только стоимость)
function change_cost(element_id, type_of_change) {
  if (type_of_change.toString() == "device_type") {
	var select_type = document.getElementById(element_id); // получаем список всех элементов (тип оборудования)
	var selected_type = select_type.options[select_type.selectedIndex].value; // получаем значение выделенного элемента (тип оборудования)
	var is_index = element_id.indexOf('/');//проверяем element id на наличие(отсутсвие) слеша с индексом
	var quantity, abonent_fee_id, cost_id;            

	
	quantity_id = "quantity" + (element_id.substring(is_index, element_id.length)).toString(); //если есть то формируем id для количества, аб платы и стоимости со слешем и индексом
	abonent_fee_id = "abonent_fee" + (element_id.substring(is_index, element_id.length)).toString();
	cost_id = "cost" + (element_id.substring(is_index, element_id.length)).toString();
	var selected_quantity = document.getElementById(quantity_id).value;// получаем значение выделенного элемента (количество)
	
	// если в количестве не число не обновляем стоимость
	t = Number(selected_quantity);
	if (Number.isNaN(t)) 
		{selected_quantity = 0;
		 }
		
  	
  }
  if (type_of_change.toString() == "quantity"){
	var selected_quantity = document.getElementById(element_id).value;
	var is_index = element_id.indexOf('/');//проверяем element id на наличие(отсутсвие) слеша с индексом
	var device_typ_id, abonent_fee_id, cost_id;
	device_type_id = "device_type" + (element_id.substring(is_index, element_id.length)).toString(); //если есть то формируем id для типа аб платы и стоимости со слешем и индексом
	abonent_fee_id = "abonent_fee" + (element_id.substring(is_index, element_id.length)).toString();
	cost_id = "cost" + (element_id.substring(is_index, element_id.length)).toString();
	var select_type = document.getElementById(device_type_id); // получаем список всех элементов (тип оборудования)
	var selected_type = select_type.options[select_type.selectedIndex].value; // получаем значение выделенного элемента (тип оборудования)
  }
  
  get = "&quantity=" + selected_quantity;
		$.ajax({
			url: "/equipment_rent/change_cost/"+selected_type+'/?'+get,
			cache: false,
			async: false,
			complete: function(html)
			{	
				var device_data = html.responseText;
				param_list = device_data.split('_');
				if (type_of_change == "device_type") {       //если менялся тип оборудования то меняем и абонентскую плату
					var ab_fee= document.getElementById(abonent_fee_id);
			    	ab_fee.innerHTML = param_list[0];}
			    var cost = document.getElementById(cost_id);  //меняем стоимость
			    cost.innerHTML = param_list[1];
			}, 
	    })
  
  calc_total_cost();		

} 	    
	    

////////////////////////////////////////////////////////////////////////
//считаем стоимость всего заказа  
function calc_total_cost() {
  var total_cost = 0;
  //считаем стоимость во всех  элементах     
  for (i=1; i<=items; i++)
 	  {     
	        var cost_temp_id = 'cost/' + i;
	        var cost_temp_elem = document.getElementById(cost_temp_id);
			if (cost_temp_elem) {
	          var cost_temp = document.getElementById(cost_temp_id).innerHTML;
	          cost_temp  = Number(cost_temp);
	          total_cost = total_cost + cost_temp; }
      }
  var total_cost_elem = document.getElementById('cost_all');
  total_cost_elem.innerHTML = total_cost;
  total_cost = 0;
  }
  	

//////////////////////////////////////////////////////////////////////////////////////////////////
//по нажатию на кнопку "Еще оборудование..." дублим элементы
function AddItem() {
var div=document.getElementById("select_device");
      
		items++;
		
		var new_itemx='\
			 <table class="type-4 modal" style = "width:500px; margin-left:30px; margin-right:30px;border-width:1px !important; border-radius:0px !important;">\
			  <tbody>\
				    <tr>\
		        	<td style = "width:250px;">\
		               <select class="value" name = "device_type" id= "device_type/'+items+'" onchange="change_cost(id, name);">\
		               </select>\
		       	    </td>\
		           <td style = "width:81px;"><font id="abonent_fee/'+items+'"></font> руб.<req>*</req></td>\
          		<td style = "width:71px; padding:7px;">\
          		<input name="quantity" id="quantity/'+items+'" type="text"  size="100" value= "1" ></input>\
          		</td>\
            <td><font id="cost/'+items+'" ></font> руб.<req>*</req></td>\
  		</tbody>\
	 </table>\
   <a style="margin-left: 5px; margin-top: -30px; position:relative; float:left;  display:inline-block; " href="javascript:void(0);" onClick="removeItem(' + items + ')"><img src=\"/media/images/sprite_delete.png\"  title=\"Удалить\"></a>'
		
		newnode=document.createElement("div");
		newnode.id = "item_" + items;
		newnode.className = "iform";
		newnode.innerHTML=new_itemx;
		div.insertBefore(newnode, null);
		
		//возращаем из базы данные по типу стоящим первым в списке и список всех типов оборудования, а также абонентскую плату
		$.ajax({
			url: "/equipment_rent/add_item/",
			cache: false,
			async: false,
		    complete: function(html)
			{	
				var data = html.responseText;
				var separate_index = data.indexOf("?");
				var device_list_unsplit = data.substring(0, separate_index);
			    var abonent_fee = data.substring(separate_index+1, data.length);
			    device_list = device_list_unsplit.split('~');
			    //записываем в элемент selct (device_type) список типов оборудования
			    select_obj = document.getElementById("device_type/" + items.toString()); 
				for (var i=0; i < device_list.length-1; i++) {
						device_list_decomosed = device_list[i].split('#');
					    select_obj.options[select_obj.options.length] = new Option(device_list_decomosed[1], device_list_decomosed[0]);
			    }
				//записываем в элемент abonent_fee значение абонентской платы
				abonent_fee_obj=document.getElementById("abonent_fee/" + items.toString());
				abonent_fee_obj.innerHTML = abonent_fee;
				//записываем в элемент cost стоимость 
				cost_obj=document.getElementById("cost/" + items.toString());
				cost_obj.innerHTML = abonent_fee;
			}, 
	    });

	  
	  //добавим обработчик для обновления стоимости по смене количества
	  id_quant  = "quantity/" +items;
	  id_cost = "cost/" +items;
	  input=document.getElementById(id_quant);
	  input.oninput = function fun() {
	  id = document.activeElement.id;
	  value = document.activeElement.value;
		   	if  (!numeric(value)) { //проверим на наличие букв и др символов(убрать минус)
			  cur_id = document.activeElement.id;
			  cur_cost_st = cur_id.split('/');
			  cur_cost = "cost/" + cur_cost_st[1];
			  document.getElementById(cur_cost).innerHTML = "0";
			  document.getElementById('error').innerHTML = 'Введите цифру'
			  document.getElementById('error').style.display='table-cell';
			  }
		 else {
		 change_cost(id, "quantity"); } 
	     calc_total_cost();
	     //теперь по всем элементам проверим есть ли соответсвие цифрам если нет  - фокус на перевый элемент и сообщение видимым. потом брейк.
	     for (i=1; i<=items; i++)
	 	  {     
		        var quan_temp_id = 'quantity/' + i;
		        var quan_temp_elem = document.getElementById(quan_temp_id);
				
				if (quan_temp_elem) { //если не был удален 
					if (!numeric(document.getElementById(quan_temp_id).value))
						 {
						  document.getElementById(quan_temp_id).focus();
						  document.getElementById('error').innerHTML = 'Введите цифру'
						  document.getElementById('error').style.display='table-cell';
						  break;}
					else
						{
						document.getElementById('error').style.display='none';
						}
		        }
	      }
	     
	  }//конец функции oninput
  calc_total_cost();
  


	  
	  
	  
/////////////// добавляем полосу прокрутки
	  var h = $('#id_popup').height();
	  var h1 = $(window).height();
	  var stpx = h1.toString() + "px";
	  if (h1-h<0)
		  {  
		  	  $('#my').css("overflow-y", "scroll");
		  	  $('#my').css("height", stpx);}
  
}	//конец функции additem




/////////////////////////////////////////////////////////////////////////
//function numeric (str) { return /^[0-9-\+\(\)\s]+z/.test(str + "z"); }
function numeric (str) { return /^[0-9(\)\s]+z/.test(str + "z"); }
//////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////	
//убираем элементы управления 
function removeItem(q){ 
	var item = document.getElementById("item_" + q);
	var parent = document.getElementById('select_device');
	parent.removeChild(item);
	calc_total_cost();
	
	//убираем полосу прокрутки
	$('#my').css("height", "auto");
	  var h = $('#id_popup').height();
	  var h1 = $(window).height();
	  var stpx = h1.toString() + "px";
	  if (h1-h<0)
		  {  
		  	  $('#my').css("overflow-y", "scroll");
		  	  $('#my').css("height", stpx);}                                        
	  
	  if (h1-h>0)
	  {  
		  $('#my').css("overflow-y", "hidden");
	  	  $('#my').css("height", "auto");}    
   
}