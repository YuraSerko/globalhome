$(function() {	
		//Left Menu Cabinet
		$('.hide_t').each(function(){
    var hi  = $(this);
    tel = $('.telefon', this);
    inter = $('.internet', this);
    data_c = $('.data_c', this);
    ul_t = $('.hide_ul_t', this);
    ul_i = $('.hide_ul_i', this);
    ul_d = $('.hide_ul_d', this);
    i =  $('.head', this);
    i_i =  $('.head_i', this);
    i_d =  $('.head_data', this);
    work = $('.work', this);
    i_w  = $('.head_work', this);
    ul_w = $('.hide_ul_w', this);
    i.click(function(){
     if (ul_t.hasClass('ul-opened') ){
        ul_t.removeClass('ul-opened');
        
        i.addClass('i_close');
        
        ul_t.stop(true,true).slideUp('slow');
       
      }
                      
    
      else if(i.hasClass('i_close')) {
      	 ul_t.addClass('ul-opened');
        i.removeClass('i_close');       
        ul_t.stop(true, true).slideDown('slow');
      }
      //return false 
      
             
     });

      tel.click(function(){ //& ul_i.hasClass('ul-opened') & ul_d.hasClass('ul-opened')
           if (ul_t.hasClass('ul-opened') ){
        ul_t.removeClass('ul-opened');
        
        i.addClass('i_close');
        
        ul_t.stop(true,true).slideUp('slow');
       
      }
                      
    
      else if(i.hasClass('i_close')) {
      	 ul_t.addClass('ul-opened');
        i.removeClass('i_close');       
        ul_t.stop(true, true).slideDown('slow');
      }
      //return false 
      
             
     });
      i_i.click(function(){
    	   if (ul_i.hasClass('ul-opened')) {
        ul_i.removeClass('ul-opened');
      
        i_i.addClass('i_close');
        
        ul_i.stop(true,true).slideUp('slow');
       
      }
   
      else if(i_i.hasClass('i_close')) {
      	 ul_i.addClass('ul-opened');
        i_i.removeClass('i_close');       
        ul_i.stop(true, true).slideDown('slow');
      }
      //return false 
     
            });

        inter.click(function(){
           if (ul_i.hasClass('ul-opened')) {
        ul_i.removeClass('ul-opened');
      
        i_i.addClass('i_close');
        
        ul_i.stop(true,true).slideUp('slow');
       
      }
   
      else if(i_i.hasClass('i_close')) {
      	 ul_i.addClass('ul-opened');
        i_i.removeClass('i_close');       
        ul_i.stop(true, true).slideDown('slow');
      }
      //return false 
     
            });
        i_w.click(function(){
        	if (ul_w.hasClass('ul-opened') ) {
        
        ul_w.removeClass('ul-opened');
       
        i_w.addClass('i_close');
        
        ul_w.stop(true, true).slideUp('slow');
      }
    
      else if(i_w.hasClass('i_close')) {
      	 ul_w.addClass('ul-opened');
        i_w.removeClass('i_close');       
        ul_w.stop(true, true).slideDown('slow');
      }
      //return false 
            });
        i_d.click(function(){
        	if (ul_d.hasClass('ul-opened') ) {
        
        ul_d.removeClass('ul-opened');
       
        i_d.addClass('i_close');
        
        ul_d.stop(true, true).slideUp('slow');
      }
    
      else if(i_d.hasClass('i_close')) {
      	 ul_d.addClass('ul-opened');
        i_d.removeClass('i_close');       
        ul_d.stop(true, true).slideDown('slow');
      }
      //return false 
            });
        data_c.click(function(){
            if (ul_d.hasClass('ul-opened') ) {
        
        ul_d.removeClass('ul-opened');
       
        i_w.addClass('i_close');
        
        ul_d.stop(true, true).slideUp('slow');
      }
      else if(i_w.hasClass('i_close')) {
      	 ul_d.addClass('ul-opened');
        i_w.removeClass('i_close');       
        ul_d.stop(true, true).slideDown('slow');
      }
      //return false 
            });
       work.click(function(){
            if (ul_w.hasClass('ul-opened') ) {
        
        ul_w.removeClass('ul-opened');
       
        i_w.addClass('i_close');
        
        ul_w.stop(true, true).slideUp('slow');
      }
      else if(i_w.hasClass('i_close')) {
      	 ul_w.addClass('ul-opened');
        i_w.removeClass('i_close');       
        ul_w.stop(true, true).slideDown('slow');
      }
      //return false 
            });  
        
        
        
       
  });

	// NoJS
	$('html').removeClass('nojs');

	// Stripes
	$('table.type-1, table.type-2, table.type-3, table.modal, .priority').each(function(){
		var t = $(this);
		t.find('tr:odd').addClass('odd').end().find('li:odd').addClass('odd');
	});

	// Fl
	$('.fl').each(function(){
		var fl  = $(this),
			fli = $('.fl-item',this),
			del = fli.find('.link-del');
		del.on('click',function(){
			$(this).parent(fli).fadeOut(100,function(){
				$(this).remove()
			});
			return false
		});
	});

	// Datepicker
	$('.datepicker').datepicker({
		firstDay: 1 ,
		changeMonth: true,
      	changeYear: true,
      	showOtherMonths: true,
      	showButtonPanel: true,
      	closeText: 'Ок',
      	currentText: 'Сегодня',
		dateFormat: 'dd.mm.yy',
		dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
		monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
		monthNamesShort: ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
	});
	
	id_date_from = $("#id_date_from").attr('value');
	id_date_to = $("#id_date_to").attr('value');
	$('#id_date_from').datepicker('setDate', id_date_from);
	$('#id_date_to').datepicker('setDate', id_date_to);

	// Tooltip
	$('.tooltip').each(function(){
		var tt  = $(this),
			tti = $('i', this),
			ttb = $('.tooltip-i',this);
		tti.hover(
			function(){ tt.find(ttb).fadeIn('fast') },
			function(){ tt.find(ttb).fadeOut('fast') }
		);
	});
	
	// Tooltip
	$('.tooltip_div').each(function(){
		var tt  = $(this),
			tti = $('div', this),
			ttb = $('.tooltip-i',this);
		tti.hover(
			function(){ tt.find(ttb).fadeIn('fast') },
			function(){ tt.find(ttb).fadeOut('fast') }
		);
	});
	
	// Details
	$('.details-item').each(function(){
		var di  = $(this),
			dih = $('.details-head a', this),
			dib = $('.details-body', this);

		dih.on('click',function(){
			if (di.hasClass('details-opened')) {
				di.removeClass('details-opened');
				dib.stop(true,true).slideUp('fast');
			}
			else {
				di.addClass('details-opened');
				dib.stop(true,true).slideDown('fast');
			}
			return false
		});
	});
	
	// Select
	$(".js-sel").each(function(){
		var sel = $(this).wrap("<div class='js-sel-wrap'></div>"),
			options = $("option", sel),
			wrap = sel.parent(),
			head = $('<span class="js-sel__head"><span></span><i class="js-sel__darr"></i></span>').prependTo(wrap),
			head_txt = $("span", head).text(selGetTxt(sel)),
			w = wrap.width();
		
		$(window).bind("load", function(){
			options.each(function(){
				head_txt.text($(this).text());
				wrap.css({'width':'auto'});
				if (wrap.width() > w) {
					w = wrap.width();
				}
				wrap.width(w);
			});
		});
			
		head_txt.text(selGetTxt(sel));
			
		sel.on('change keyup', function(){
			head_txt.text(selGetTxt(sel));
		});

	});

	function selGetTxt(sel) {
		var ret = "";
		$("option", sel).each(function(){
			
			if ($(this).attr("selected") || this.selected) {
				ret = $(this).text();
			}
		});
		return ret;
	}
	
	//left menu in private page
	$(".navside>ul>li").each(function() {
		$(".navside>ul>li").mouseover(function(){
			$(this).stop().animate({"margin-left":"15"}, 150)
			});
		$(".navside>ul>li").mouseout(function(){
			$(this).stop().animate({"margin-left":"0"}, 150)
			});
	});

	


});