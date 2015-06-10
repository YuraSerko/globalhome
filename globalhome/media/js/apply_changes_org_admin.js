
(function($) {
    $(document).ready(function($) {
    	
    	// находим номер заявки
    	// получим текущий url (элементы массива, разделенные /)
    	urlarray = window.location.toString().split('/');
		zayavka_id = urlarray[urlarray.length-2]	
		
    	
    	
    	
    	if((urlarray[urlarray.length-1]) == '?notice=ok') { // показываем сообщение если ajax пошел по ветке success
    			note = '<ul class="messagelist"><li class="info">' + 'Изменения пользователя применены.' + '</li></ul>';
			    $($("[class = breadcrumbs]", document) ).after(note);    
    		}
    	
    	if((urlarray[urlarray.length-1]) == '?notice=cancel') { // показываем сообщение если ajax пошел по ветке success
			note = '<ul class="messagelist"><li class="info">' + 'Заявка отклонена.' + '</li></ul>';
		    $($("[class = breadcrumbs]", document) ).after(note);    
		}
    	
    	
    	ok = 'ok'
    	cancel = 'cancel'
    	
    	if ($('#id_applied:checked').val()!='on') { 	//добавим кнопку если не были ативированы изменения активировать изменения		
	    					
				$(".submit-row").append('<a href="#" style="margin-left: 20px;" onclick="fun(' + ok + ')">Применить пользовательские изменения</a>');
				$(".submit-row").append('<a href="#" style="margin-left: 20px;" onclick="fun(' + cancel + ')">Отклонить изменения</a>');
				
    	 } //end if
    	$(".submit-row").append('<a href="#" style="margin-left: 40px;" onclick="fun_script()">Запустить скрипт</a>');
    });
    
    
    
})(django.jQuery);

var show_notice = false;
var zayavka_id = undefined;

function fun(action)
{  
	
	// checkbox на удаление ставится только администратором
	
	
	if (action == 'ok') {
		var items = {
				zayavka_id:zayavka_id,
				u_org_name:$('#id_u_org_name').val(),
				u_org_address:$('#id_u_address').val(),
				u_org_phone:$('#id_u_phone').val(),
				u_org_url:$('#id_u_url').val(),
				u_org_hours:$('#id_u_hours').val(),
				to_del:$('#id_to_del:checked').val(),
				action:'ok',
				}
		}
	else {
		var items = {
			zayavka_id:zayavka_id,
			action:'cancel',
			}
	}
	
		$.ajax({
			url: '/admin/hotspot/mobiorganizationsuserchanges/apply_changes/',
			type: 'POST',
			data: items,
			cash: true,
			async:false,
			success: function(html){
				
				
			    
			    //переход при удачном ajax
				
			    document.location.href = window.location + '?notice=' + html
			    
			}
		 });



}
//====================================================================================
// передаем параметры для запуска 2 скриптов в python
function fun_script(){
	items = {zayavka_id:zayavka_id};
	
	note = '<ul class="messagelist"><li class="info" id = "notice_id">' + 'Скрипт начал работу ждите' + '</li></ul>';
    $($("[class = breadcrumbs]", document) ).after(note);
    
	$.ajax({
		url: '/admin/hotspot/mobiorganizationsuserchanges/start_scripts/',
		type: 'POST',
		async: true,
		data: items,
		cash: true,
		success: function(html){
			$('#notice_id').css('display', 'none');
			note = '<ul class="messagelist"><li class="info" >' + 'Скрипт закончил работу' + '</li></ul>';
		    $($("[class = breadcrumbs]", document) ).after(note);
			}
	})
	
	
	
	
}
