// JavaScript Document
function create_new_tr(el_id, el_text, cost, service_id, say_paid, date_for_paid, paid_zakaz, odd){
		if (say_paid == 'Paid')
			{	
			return '<tr class="raw'+el_id+odd+'">\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_top('+el_id+')" class="up">↑</a></td>\
            <td width="20px" style="text-align: center;"><div class="num" align="center">'+el_id+'</div></td>\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_bottom('+el_id+')" class="down">↓</a></td>\
            <td style="padding-left: 10px;"><span class="subj">'+el_text+'</span><input type="hidden" id="hidden_'+el_id+'" name="raw'+el_id+'" value="'+service_id+'"/></td>\
			<td><div class="date_for_paid" align="center" style="cursor:default;">'+date_for_paid+'</div></td>\
			<td><div class="cost" align="center" style="cursor:default;">'+cost+'</div></td>\
			<td></td>\
			<td><div class="status_div" align="center" style="cursor:default; background-color: #00CC00"><font color="#FFFFFF">Оплачено</font></div></td>\
   		    <input type="hidden" id="hidden_paid_'+el_id+'" value="'+say_paid+'"/>\
			</tr>';
			}
		if (say_paid == 'Not paid')
			{	
			return '<tr class="raw'+el_id+odd+'">\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_top('+el_id+')" class="up">↑</a></td>\
            <td width="20px" style="text-align: center;"><div class="num" align="center">'+el_id+'</div></td>\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_bottom('+el_id+')" class="down">↓</a></td>\
            <td style="padding-left: 10px;"><span class="subj">'+el_text+'</span><input type="hidden" id="hidden_'+el_id+'" name="raw'+el_id+'" value="'+service_id+'"/></td>\
			<td><div class="date_for_paid" align="center" style="cursor:default;">'+date_for_paid+'</div></td>\
			<td><div class="cost" align="center" style="cursor:default;">'+cost+'</div></td>\
			<td align="center"><input id="paid'+el_id+'" type="checkbox" name="checks" title="Выделите для оплаты" value="'+paid_zakaz+'"/></td>\
            <td><div class="status_div" align="center" style="cursor: default; background-color: #ffcf00;"><font color="#FFFFFF">Не оплачено</font></div></td>\
   		    <input type="hidden" id="hidden_paid_'+el_id+'" value="'+say_paid+'"/>\
			</tr>';	
			}
		if (say_paid == 'Block')
			{
			return '<tr class="raw'+el_id+odd+'">\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_top('+el_id+')" class="up">↑</a></td>\
            <td width="20px" style="text-align: center;"><div class="num" align="center">'+el_id+'</div></td>\
            <td width="20px" style="text-align: center;"><a style="cursor: pointer;" onclick="move_bottom('+el_id+')" class="down">↓</a></td>\
            <td style="padding-left: 10px;"><span class="subj">'+el_text+'</span><input type="hidden" id="hidden_'+el_id+'" name="raw'+el_id+'" value="'+service_id+'"/></td>\
			<td><div class="date_for_paid" align="center" style="cursor:default;">'+date_for_paid+'</div></td>\
			<td><div class="cost" align="center" style="cursor:default;">'+cost+'</div></td>\
			<td align="center"><input id="paid'+el_id+'" type="checkbox" name="checks" title="Выделите для оплаты" value="'+paid_zakaz+'"/></td>\
            <td><div class="status_div" align="center" style="cursor:default; background-color: #FF0033"><font color="#FFFFFF">Блокировка</font></div></td>\
   		    <input type="hidden" id="hidden_paid_'+el_id+'" value="'+say_paid+'"/>\
			</tr>';
			}

}//end of the function create_new_tr

function move_top(el_id){
  if(el_id!=1){
    
    //узнаем ид верхнего tr
    var top_tr_id = el_id-1;
    
    //получаем все данные верхнего tr
	var top_odd = '';
	if ( $('tr.raw'+top_tr_id).hasClass("odd") ) 
	{
		top_odd = ' odd';
	}
    var top_tr_text = $('tr.raw'+top_tr_id+' .subj').html();
	var top_cost = $('tr.raw'+top_tr_id+' .cost').html();
	var top_date_for_paid = $('tr.raw'+top_tr_id+' .date_for_paid').html();
	var top_service_id = document.getElementById('hidden_'+top_tr_id).value;
	var top_say_paid = document.getElementById('hidden_paid_'+top_tr_id).value;
	try{
		var top_paid_zakaz = document.getElementById('paid'+top_tr_id).value;
  		} 
	catch(e){
		top_paid_zakaz = '';
  		}
	try{
		var top_paid = document.getElementById('paid'+top_tr_id).checked;
  		} 
	catch(e){
		top_paid = '';
  		}
	
    //удаляем верхний tr
    $('tr.raw'+top_tr_id).remove();
	
    //получаем все данные перемещаемого элемента
	var per_odd = '';
	if ( $('tr.raw'+el_id).hasClass("odd") ) 
	{
		per_odd = ' odd';
	}
    var per_tr_text = $('tr.raw'+el_id+' .subj').html();
	var per_cost = $('tr.raw'+el_id+' .cost').html();
	var per_date_for_paid = $('tr.raw'+el_id+' .date_for_paid').html();
	var per_service_id = document.getElementById('hidden_'+el_id).value;
	var per_say_paid = document.getElementById('hidden_paid_'+el_id).value;
	try{
		var per_paid_zakaz = document.getElementById('paid'+el_id).value;
  		} 
	catch(e){
		per_paid_zakaz = '';
  		}
	 try{
		var per_paid = document.getElementById('paid'+el_id).checked;
  		} 
	catch(e){
		per_paid = '';
  		}
	
    //создаем копию перемещаемого вверх элемента над ни же с другим ид
    var newtr = create_new_tr(top_tr_id, per_tr_text, per_cost, per_service_id, per_say_paid, per_date_for_paid, per_paid_zakaz, top_odd);
    $('tr.raw'+el_id).before(newtr);
	if (per_say_paid != 'Paid')
	{
	document.getElementById('paid'+top_tr_id).checked=per_paid;
	}

    //удаляем перемещаемый элемент
    $('tr.raw'+el_id).remove();
    
    //задаем под до этого созданным элементом эелемент который был до этого над
    //перемещаемым вверх, создаем его с ид на 1 меньше
    var newtr = create_new_tr(el_id, top_tr_text, top_cost, top_service_id, top_say_paid, top_date_for_paid, top_paid_zakaz, per_odd);
    $('tr.raw'+top_tr_id).after(newtr);
	if (top_say_paid != 'Paid')
	{
	document.getElementById('paid'+el_id).checked=top_paid;
	}

    
  }//end if
  
}//end of the function move_top

function move_bottom(el_id){
     
   //узнаем количество элементов в списке
   var tr_count = $('.mylist tr').size();
  
   //проверяем не пытаемся ли мы сместить вниз последний элемент
   if(el_id!=tr_count){
  
     //узнаем порядковый номер нижнего элемента
    var bot_tr_id = el_id+1;
    
    //получаем все данные элемента расположенного под перемещаемым
	var bot_odd = '';
	if ( $('tr.raw'+bot_tr_id).hasClass("odd") ) 
	{
		bot_odd = ' odd';
	}
    var bot_tr_text = $('tr.raw'+bot_tr_id+' .subj').html();
    var bot_tr_cost = $('tr.raw'+bot_tr_id+' .cost').html();
	var bot_date_for_paid = $('tr.raw'+bot_tr_id+' .date_for_paid').html();
	var bot_service_id = document.getElementById('hidden_'+bot_tr_id).value;
	var bot_say_paid = document.getElementById('hidden_paid_'+bot_tr_id).value;
	try{
		var bot_paid_zakaz = document.getElementById('paid'+bot_tr_id).value;
  		} 
	catch(e){
		bot_paid_zakaz = '';
  		}
	try{
		var bot_paid = document.getElementById('paid'+bot_tr_id).checked;
		}
	catch(e){
		bot_paid = '';
		}
	
    //удаляем елемент расположенный под перемещаемым
    $('tr.raw'+bot_tr_id).remove();
     
	//получаем все данные перемещаемого элемента
	var per_odd = '';
	if ( $('tr.raw'+el_id).hasClass("odd") ) 
	{
		per_odd = ' odd';
	}
    var per_tr_text = $('tr.raw'+el_id+' .subj').html();
	var per_tr_cost = $('tr.raw'+el_id+' .cost').html();
	var per_date_for_paid = $('tr.raw'+el_id+' .date_for_paid').html();
	var per_service_id = document.getElementById('hidden_'+el_id).value;
	var per_say_paid = document.getElementById('hidden_paid_'+el_id).value;
	try{
		var per_paid_zakaz = document.getElementById('paid'+el_id).value;
  		} 
	catch(e){
		per_paid_zakaz = '';
  		}
	 try{
		var per_paid = document.getElementById('paid'+el_id).checked;
  		} 
	catch(e){
		per_paid = '';
  		}
	
    //создаем копию перемещаемого вниз элемента под ним же с другим ил +1
    var newtr = create_new_tr(bot_tr_id, per_tr_text, per_tr_cost, per_service_id, per_say_paid, per_date_for_paid, per_paid_zakaz, bot_odd);
    $('tr.raw'+el_id).after(newtr);
	if (per_say_paid != 'Paid')
	{
	document.getElementById('paid'+bot_tr_id).checked=per_paid;
	}
	 
    //удаляем перемещаемый элемент
    $('tr.raw'+el_id).remove();
     
    //создаем над созданным элементом копию элемента который был расположен под
    //перемещаемым элементом
    var newtr = create_new_tr(el_id, bot_tr_text, bot_tr_cost, bot_service_id, bot_say_paid, bot_date_for_paid, bot_paid_zakaz, per_odd);
    $('tr.raw'+bot_tr_id).before(newtr);
	if (top_say_paid != 'Paid')
	{
	document.getElementById('paid'+el_id).checked=bot_paid;
	} 
	 
   }//end if
    
}//end function move_bottom


function all_change()
{
  var check = document.getElementById('all_checkbox').checked;
  for(var i=0;i<document.form_priority.checks.length;i++)
	 document.form_priority.checks[i].checked = check;
}