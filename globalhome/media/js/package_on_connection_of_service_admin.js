
(function($) {
    $(document).ready(function($) {
    	
    	//значение поля id_slugs_document_admin и adm_act
    	var admin_slug = $('#id_slugs_document_admin').val();
    	var adm_act = $("#id_activate_admin").attr("checked");
    	var deact = $("#id_deactivate").attr("checked");
    	if ((admin_slug == 'akt_priema_peredachi_oborudovaniya_spisok') && (adm_act==false) && (deact==false))
    	
		//pack_id
		{ 	var pidstring = window.location.toString();
			pidarray = pidstring.split('/');
			pidarray_length  = pidarray.length;
			pack_id = pidarray[pidarray_length-2]
			get = "&pack_id=" + pack_id;
		
			
			download_doc = "'/admin/findocs/package_on_connection_of_service/download_findoc_admin?pack_id=" +pack_id +   "'";
			$(".submit-row").append('<a href='+download_doc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Акт приема-передачи оборудования</a>');
	  	
			//активировать пакет
			sign_doc = "'/admin/findocs/package_on_connection_of_service/sign_findoc_admin?pack_id=" +pack_id + "'";
			$(".submit-row").append('<a href='+sign_doc+' class="addlink" id="add_id_address_dc" style="margin-left: 20px;" onclick="return showAddAnotherPopup(this);">Активировать пакет</a>');
		}
    	
    	//выводим сообщение о сформированных заказах или о том что их не удалось сформировать
    	href_cur = window.location.toString();
    	if   ((href_cur.indexOf('?complete=true')) !=-1)
    		{    		
    		  var url_to_go = href_cur.substr(0, href_cur.indexOf('?complete=true')); //    		  
		      note = '<ul class="messagelist"><li class="info">' + 'Договор успешно подписан. Заказы сформированы успешно.' + '</li></ul>';
		      $($("[class = breadcrumbs]", document) ).after(note);	      
    		}
    	if   ((href_cur.indexOf('?complete=false')) !=-1)
		{    		
		  var url_to_go = href_cur.substr(0, href_cur.indexOf('?complete=true')); // 	  
	      note = '<ul class="messagelist"><li class="info">' + 'Договор подписать не удалось. Заказы не сформированы.' + '</li></ul>';
	      $($("[class = breadcrumbs]", document) ).after(note);	      
		}

    	
    });
})(django.jQuery);

