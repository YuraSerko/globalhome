function slide(){


	var pull 		= $('#pull');
		menu 		= $('nav ul');
		menuHeight	= menu.height();

	$(pull).on('click', function(e) {
		e.preventDefault();
		menu.slideToggle();
	});
/*
	$(window).resize(function(){
      		var w = $(window).width();
      		if(w > 320 && menu.is(':hidden')) {
      			menu.removeAttr('style');
      		}
  		});
  		*/
//if($('.searchbox').val() != ''){alert('123');}
/*
$('#ya_input').blur(function(){
if($('#ya_input').val() != ''){
$('#ya_input').css("background-image","none")
}
else{

$('#ya_input').css('background-image',' url("/media/images/yandex-for-white-background.png")')

}

})
 */
$('.dot').click(function () {
			$(this).parent().find('ul').slideToggle()
	
    });

$('.searchbox').on('keyup', function() {
		if($('.searchbox').val().length > 0)
        {
            $(this).css('background-image','none');}	
	
                   else{
                    $(this).css('background-image','url("/media/images/yandex-for-white-background.png")');
					$(this).css('background-repeat','no-repeat')
					$(this).css('background-position', '7px 9px')
					;
                   }
                }  );
 
if($('#loginform').children().length < 3){
	$('.side_h1').css({'position':'relative','top':'25px','margin':'0 auto','display':'block '});
	$('#loginform').css('height','auto');

}
}