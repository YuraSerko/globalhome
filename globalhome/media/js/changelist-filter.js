// Fancier version https://gist.github.com/985283 

;(function($){ $(document).ready(function(){
    $('#changelist-filter').children('h2').each(function(){
        var $title = $(this);
        $title.click(function(){
        	$('#changelist-filter').children('h3').slideToggle();
        	$('#changelist-filter').children('h3').next().slideToggle();
        });
    });   
  });
})(django.jQuery);