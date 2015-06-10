            

//========================My_Map==============

window.onload = function(){
		var t = document.getElementById('td_4link_1');
		if( t ){
		cont = document.getElementById('my_map');
		cont.style.margin = '39px 0 0 29px';
		//$('#my_map:after').css('position','relative')
		}else
		{
				cont = document.getElementById('my_map');
			if(cont){
		
		cont.style.margin = '93px  0  100px 29px';
		}
		//$('#my_map:after').css('margin','0px')
		
		//$('#my_map:after').css('margin-top', ' -300px');
		//$('.contacts:after').css('top', ' 340px');
		
		//var p   = querySelectorAll('.page-inner2')
		//alert(p)
		//p.style.opacity = '0';
		}
};
	//========Dostup k .page-inner2=======
		//$(function() {
		//$('.page-inner2').css('background', 'none');
		//$('.under-construction').css('height', ' 932px');
		//});
	
		//$("input").click(function(){
		//	$('INPUT#id_captcha_1.captcha-input').css('background', ' white');
			//});

$(function() {
// Text inputs
	$('.popup-form .text, .web-phone-f .text').each(function(){
		var val = $(this).val().trim();
		if (val != ''){
			$(this).addClass('text-done');
		}
		$(this).blur(function(){
			var val = $(this).val().trim();
			if (val != ''){
				$(this).addClass('text-done');
			}
			else {
				$(this).removeClass('text-done');
			}	
		});
	});
	//============================================
	

		// Layout========Otvechaet za navside menu otkritie po ssilke===========
	/*$(window).bind('load resize', layout);
	layout();
	function layout(){
		if ($(window).width() < 1160) {
			$('body').addClass('body-narrow');
		}
		else {
			$('body').removeClass('body-narrow');
		}
	}*/
	/*=================*/
	
	
	
		
	//=========================================
	//============================== Popup =====================================
	$('.js-link-login').on('click',function(){
		$('.tint, .popup').fadeIn('fast');
		$('.login-form').find('input:first').focus();
		return false
	});

	$('.js-link-register').on('click',function(){
		$('.tint, .popup').fadeIn('fast');
		$('.register-form').find('input:first').focus();
		return false
	});

	$('.tint, .icon-close').on('click',function(){
		$('.tint, .popup').fadeOut(100);
		return false
	});

	$(document).keyup(function(e) {
		if (e.keyCode == 27) {
			$('.tint, .popup').fadeOut(50);
		}
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
	// Stripes
	$('table.type-1, table.type-2, table.type-3, table.modal').each(function(){
		var t = $(this);
		t.find('tr:odd').addClass('odd').end().find('li:odd').addClass('odd');
		
	});
	
	// NoJS
	$('html').removeClass('nojs');

	/* Navside
	$('.navside').each(function(){
		var ns   = $(this),
			drop = $('.multiple > i');

		drop.on('click',function(){
			$(this).parent().find('ul').stop(true,true).slideToggle('fast');
			$(this).parent().toggleClass('opened');
			
			article = document.getElementById('aside_Menu');
			article.style.padding = ' 248px 0 300px 0';
			if (opened == true){
				
				$(this).parent().find('ul.only2').stop(true,true).slideToggle('fast');
				
				}
			
		});
	});*/
			
			
			// Navside
	$('.navside').each(function(){
		var ns   = $(this),
			drop = $('.multiple > i');
			//drop2 = $('.multiple3 > i');

		drop.on('click',function(){
		//$(this).parent().find('ul.only').stop(true,true).slideToggle('fast');
		
			opened = $(this).parent().hasClass('opened');
			$(this).parent().parent().find('.opened').removeClass('opened');
			$(this).parent().parent().find('.open_ul').removeClass('open_ul');
																	
			//$('.cols').css('margin', ' 0 0 500px ');					//!!!======Bivshiy padding===Do 20.11.13
			
			article = document.getElementById('aside_Menu');
			article.style.padding = ' 248px 0 300px 0'; 
			//article.style.margin = ' 0px 0 60px 0'; 
			$('#Moscow_crane').css('top','315px');
			
			$('#article_Menu.section div#Moscow_crane h1.title').css('margin-top','-234px');
			
			//$('.under-construction').css('margin','0 0 6px');
				
					//$('.under-construction').css('margin-bottom', ' -180px'); Хреново работает
			//construct = document.getElementById('construction');
			//construct.style.height = '10';
				//$('.under-construction').css('height', ' 932px');
			if (opened == false) {
				$(this).parent().addClass('opened');
				$(this).parent().children('ul').addClass('open_ul');}
				/*if ( opened == true){
				
			
				$(this).parent().find('ul.only2').stop(true,true).slideToggle('fast');
				
				}*/
		});
	});
		$("[href='#']").click(function(){

			opened = $(this).parent().hasClass('opened');
			$(this).parent().parent().find('.opened').removeClass('opened');
			$(this).parent().parent().find('.open_ul').removeClass('open_ul');
			if (opened == false) {
				$(this).parent().addClass('opened');
				$(this).parent().children('ul').addClass('open_ul');}
			
			
		});
		

		/*=========== #Zakaz====================*/
$("[href='#zakaz']").click(function(){
	//$('.page-inner2').css('background', 'url(../images/wall.png) repeat-x 47% 100%');
var head = document.querySelector('header')
head.style.position = 'static';
var footer = document.getElementById('footer_my')//поменять свойство, чтобы футер не мешал
footer.style.display = 'none';	
var hot = document.getElementById('hottlin')
hot.style.display = 'none';

 $('.page-inner2').css('background', 'url(/media/images/wall.png) repeat-x 47% 100%');
  $('.footer').css('position', 'static');

});


$("[href='#close']").click(function(){

var head = document.querySelector('header');
head.style.position = 'relative';
var footer = document.getElementById('footer_my')//поменять свойство, чтобы футер не мешал
footer.style.display = 'block';
var hot = document.getElementById('hottlin')
hot.style.display = 'block';
$('.footer').css('position', 'relative');
 $('.page-inner2').css('background', 'none');

});
/*Клик по оверлею возвращает прежние свойства*/
$('.overlay').click(function(){
		var head = document.querySelector('header');
head.style.position = 'relative';
var footer = document.getElementById('footer_my')//поменять свойство, чтобы футер не мешал
footer.style.display = 'block';
var hot = document.getElementById('hottlin')
hot.style.display = 'block';
$('.footer').css('position', 'relative');
 $('.page-inner2').css('background', 'none');
});


	
	/*====================== Text inputs
	$('.popup-form .text, .web-phone-f .text').each(function(){
		var val = $(this).val().trim();
		if (val != ''){
			$(this).addClass('text-done');
		}
		$(this).blur(function(){
			var val = $(this).val().trim();
			if (val != ''){
				$(this).addClass('text-done');
			}
			else {
				$(this).removeClass('text-done');
			}	
		});
	});
	===================================================*/
	// Toggle
	$('.toggle-item').each(function(){
		var ti   = $(this),
			tih  = $('.toggle-head', this),
			tiht = tih.text(),
			tib  = $('.toggle-body', this);

		tih.attr('title', tiht);

		tih.filter('.toggle-drop').on('click',function(){
			if (ti.hasClass('toggle-opened')) {
				ti.removeClass('toggle-opened');
				tib.fadeOut('fast');
			}
			else {
				ti.addClass('toggle-opened').siblings().removeClass('toggle-opened').find('.toggle-body').fadeOut('fast');
				tib.fadeIn('fast');
			}
			return false
		});
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

	
 /* $('#add-group-button').click(function(){
            	
            		
            		$('.header').css('position', 'static')
            		alert('ok');
            
            });*/
	// Web-phone
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

	$('.web-phone-remove').click(function(){
		var wpn = $('#wpn');
		wpn.val( wpn.val().slice(0,-1) );
	});

	$('#wpn').keyup(function() {
		webPhoneInputCheck()
	});

	$('.web-phone-numpad input').click(function() {
		webPhoneInputCheck()
	});

 $('#my_map').each(function(){
  	$(this).addClass('yandex');
  
  }); 

});/*function*/

