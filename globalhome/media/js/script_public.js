$(function() {
	
	// Stripes
	$('table.type-1, table.type-2, table.type-3, table.modal').each(function(){
		var t = $(this);
		t.find('tr:odd').addClass('odd').end().find('li:odd').addClass('odd');
	});
	
	// NoJS
	$('html').removeClass('nojs');

	// Layout
	$(window).bind('load resize', layout);
	layout();
	function layout(){
		if ($(window).width() < 1160) {
			$('body').addClass('body-narrow');
		}
		else {
			$('body').removeClass('body-narrow');
		}
	}
	
	$(document).each(function(){

		if($('[name]').is('[name = key]')) {
			var pathname = $('[name = key]').val()
			var $a = $('.navside [href $="/'+pathname+'/"]');
			}
		else{
			var pathname = window.location.pathname;
			var $a = $('.navside [href ="'+pathname+'"]');
			}
		
		$a.addClass('active');
		$a.parents('li.multiple').addClass('opened');
		$a.parents('ul').addClass('open_ul');
		var $par = $a.parent('li.multiple');
		$par.children('ul').addClass('open_ul');
		});
	
	
	// Navside
	$('.navside').each(function(){
		var ns   = $(this),
			drop = $('.multiple > i');

		drop.on('click',function(){
			opened = $(this).parent().hasClass('opened');
			$(this).parent().parent().find('.opened').removeClass('opened');
			$(this).parent().parent().find('.open_ul').removeClass('open_ul');
			if (opened == false) {
				$(this).parent().addClass('opened');
				$(this).parent().children('ul').addClass('open_ul');}
		});
	});
	
	   
		$("[href='#']").click(function(){
			opened = $(this).parent().hasClass('opened');
			$(this).parent().parent().find('.opened').removeClass('opened');
			$(this).parent().parent().find('.open_ul').removeClass('open_ul');
			if (opened == false) {
				$(this).parent().addClass('opened');
				$(this).parent().children('ul').addClass('open_ul');}
			
			
		})
		
		
		
	// Popup
	$('.link-login').on('click',function(){
		$('.tint, .popup').fadeIn('fast');
		$('.login-form').find('input:first').focus();
		return false
	});

	$('.link-register').on('click',function(){
		$('.tint, .popup').fadeIn('fast');
		$('.register-form').find('input:first').focus();
		return false
	});

	$('.tint, .popup-close').on('click',function(){
		$('.tint, .popup').fadeOut(100);
		return false
	});

	$(document).keyup(function(e) {
		if (e.keyCode == 27) {
			$('.tint, .popup').fadeOut(50);
		}
	});

	// Toggle
	$('.toggle-item').each(function(){
		var ti  = $(this),
			tih = $('.toggle-head', this),
			tib = $('.toggle-body', this);

		tih.filter('.toggle-drop').on('click',function(){
			if (ti.hasClass('toggle-opened')) {
				ti.removeClass('toggle-opened');
				tib.fadeOut('fast');
			}
			else {
				ti.addClass('toggle-opened').siblings().removeClass('toggle-opened').find('.toggle-body').fadeOut(100);
				tib.fadeIn('fast');
			}
			return false
		});
	});
	
		// Forgot
	$('.popup-form-forgot-h').on('click',function(){
			$(this).find('span').toggle();
			if ($(this).parent().hasClass('popup-form-forgot-opened')) {
				$(this).parent().removeClass('popup-form-forgot-opened');
				$('.popup-form-forgot-i').stop(true,true).slideUp('fast');
			}
			else {
				$(this).parent().addClass('popup-form-forgot-opened');
				$('.popup-form-forgot-i').stop(true,true).slideDown('fast');
			}
			return false
		});
		
	// Web-phone
	// input text size
	function webPhoneInputCheck(){
		var webPhoneInput = $('#wpn'),
			webPhoneInputText = webPhoneInput.val().length;

		if (webPhoneInputText > 15){
			webPhoneInput.addClass('long');
		}
		else {
			webPhoneInput.removeClass('long');
		}		
	}

	$('#wpn').keyup(function() {
		webPhoneInputCheck()
	});

	$('.web-phone-numpad input').click(function() {
		webPhoneInputCheck()
	});


});

	//news
$(function(){
    $(".item_news").click(function(){
      	show = $(this).hasClass('show')
    	//$(this).addClass('show')
    	$(this).parent().find('.show').removeClass('show');
		if (show == false) {
			$(this).addClass('show');}
			})})