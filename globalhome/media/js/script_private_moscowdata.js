$(function() {

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
	
	 /*Tooltip
	$('.tooltip_div').each(function(){
		var tt  = $(this),
			tti = $('div', this),
			ttb = $('.tooltip-i',this);
		tti.hover(
			function(){ tt.find(ttb).fadeIn('fast') },
			function(){ tt.find(ttb).fadeOut('fast') }
		);
	});*/
	
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
//=================================================================My TAB Change=====================
