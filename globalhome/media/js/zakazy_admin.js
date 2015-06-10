function new_window(url)
{
var leftvar = (screen.width-600)/2;
var topvar = (screen.height-600)/2;

window.open(url,'newwin','top='+topvar+', left='+leftvar+', menubar=0, toolbar=0, location=0, directories=0, status=0, scrollbars=1, resizable=0, width=600, height=600');
}

function send_message(zakaz_id)
{
	$.ajax({
			url: "/admin/data_centr/zakazy/send_message_about_server/"+zakaz_id+"/",
			cache: false,
			async: false,
			  
			success: function(status){
				
				alert('Сообщение успешно отправлено');
				  
			}  
		});
}

function calculate_cost(zakaz_id)
{
	$.ajax({
			url: "/admin/data_centr/zakazy/calculate_cost/"+zakaz_id+"/",
			cache: false,
			async: false,
			  
			success: function(cost){
				qu = confirm('Стоимость успешно пересчитана. \nНовая стоимоть = ' + cost + '\nПрименить новую стоимость?');
				if (qu) {
					$('#id_cost').val(cost);
				}
				  
			}  
		});
}

function restore_zakaz(zakaz_id, disconnected)
{	
	zakaz_id = $(".field-id").find('div').find('p').text()
	if (disconnected) {
		qu = confirm('Вы действительно хотите восстановить заказ?\nПодтверждение перенаправит Вас на страницу восстановления!');
		if (qu) {
			window.open('/admin/data_centr/restore_zakaz/?zakaz_id='+zakaz_id, '_blank');
		}
	}
	else {
		qu = confirm('ДАННЫЙ ЗАКАЗ ЯВЛЯЕТСЯ ДЕЙСТВУЮЩИМ!\n\nВы действительно хотите восстановить заказ?\nПодтверждение перенаправит Вас на страницу восстановления!');
		if (qu) {
			window.open('/admin/data_centr/restore_zakaz/?zakaz_id='+zakaz_id, '_blank');
		}
	}
}
function activate_zakaz(zakaz_id){

    $.ajax({
            type: "GET",
            data:{zayavka_id:zakaz_id},
            url: "/account/internet/demands/activation2/",
            success:function(data){
               if(data!="ipless")
                   //console.log(data)
                   location.reload()
               else alert("К сожалению мы не можем выдать такое количество IP-адресов!")
            },
            error:function(data){
                //console.log(data.responseText)
            }
        });
}



function print_doc(zakaz_id){
    window.open('/admin/findocs/print_act/?zakaz_id='+zakaz_id, '_blank');
}
(function($) {
    $(document).ready(function($) {
		zakaz_id = $(".field-id").find('div').find('p').text()
		var  service_type_id = $('#id_service_type').val();
		var deact_date = $("#id_date_deactivation_0").val();
		
		//if ($.inArray($("#id_service_type").val(), [2, 11])) {
		if (  $("#id_service_type").val() ==  2  ||   $("#id_service_type").val() ==  11  ) {
		$("#add_id_address_dc").remove();
		$(".field-id").css('display','None');
		find_place_in_dc = "'/admin/data_centr/zakazy/search_place_in_dc/"+zakaz_id+"/'";
		edit_place_in_dc = "'/admin/data_centr/zakazy/search_place_in_dc/"+zakaz_id+"/?edit=True'";
      /*  $(".field-address_dc").find('div').append('<a href="javascript: new_window('+find_place_in_dc+')" class="addlink" style="margin-left: 20px;">Найти место в ДЦ</a><a href="javascript: new_window(/qwe/)" class="addlink" style="margin-left: 20px;">Добавить адрес в ДЦ</a>');*/
		
        $(".field-address_dc").find('div').append('<a href='+find_place_in_dc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Новое место в ДЦ</a>');
        $(".field-address_dc").find('div').append('<a href='+edit_place_in_dc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Редактировать текущее место в ДЦ</a>');
		$(".field-address_dc").find('div').append('<a href=# class="addlink" id="send_message" style="margin-left: 20px;" onclick="send_message('+zakaz_id+')">Отправить пользователю сообщение</a>');
		}
		
		
		
		$(".field-cost").find('div').append('<input type="button" onclick="calculate_cost('+zakaz_id+')" value="Пересчитать стоимость">');
		if ($('#id_date_deactivation_0').val()) {
			$(".submit-row").append('<input type="button" class="default" onclick="restore_zakaz('+zakaz_id+', 1)" value="Восстановить заказ" style="background:#0C6;border: 2px solid #090">');
		}
		else {
			$(".submit-row").append('<input type="button" class="default" onclick="restore_zakaz('+zakaz_id+', 0)" value="Восстановить заказ" style="background:#F66;border: 2px solid #F00">');
		}
        if($("#id_status_zakaza").val()!=2)	    $(".submit-row").append('<input type="button" class="default" onclick="activate_zakaz('+zakaz_id+')" value="Активировать заказ" style="background:lime;border: 2px solid green">');
        $(".submit-row").append('<input type="button" class="default" onclick="print_doc('+zakaz_id+')" value="Акт приемки/передачи" style="background:#ccc;border: 2px solid #999">');
		
		if ((service_type_id==13) && (deact_date != '')) {
		// кнопки для скачивания и подписания документа на передачу оборудования обратно globalhome
	    var pack_id = $('#id_pack_id').val();
		//скачать документ 
		download_doc = "'/admin/data_centr/zakazy/download_findoc_zakazy_admin/1/?zakaz_id=" + zakaz_id +  "'";
		$(".submit-row").append('<a href='+download_doc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Скачать договор</a>'); 	
		//подписать документ
		sign_doc = "'/admin/data_centr/zakazy/sign_findoc_zakazy_admin/1/1/?zakaz_id=" + zakaz_id +  "'";  //действие 1(отобразить документ), документ по счету 1
		$(".submit-row").append('<a href='+sign_doc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Подписать договор</a>');
		}
		//cообщение об удачном расторжении
		href_cur = window.location.toString();
    	if   ((href_cur.indexOf('?complete=true')) !=-1)
    		{    		
    		  var url_to_go = href_cur.substr(0, href_cur.indexOf('?display=true')); // 
		      note = '<ul class="messagelist"><li class="info">' + 'Договор успешно подписан.' + '</li></ul>';
		      $($("[class = breadcrumbs]", document) ).after(note); 
    		}
    	
    	if   ((href_cur.indexOf('?complete=false')) !=-1)
		{    		
		  var url_to_go = href_cur.substr(0, href_cur.indexOf('?display=true')); // 
	      note = '<ul class="messagelist"><li class="info">' + 'Договор подписать не удалось.' + '</li></ul>';
	      $($("[class = breadcrumbs]", document) ).after(note);
	      
		}
		
		
    });
})(django.jQuery);