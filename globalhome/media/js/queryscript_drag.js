



$(document).ready(function(){
	/*$(function(){                       // после загрузки страницы
	   $('#push_id').click(function(){// на нажатие h1 вешаем обработчик, который
		 $('#toggler').toggle('slow');        // у элемента с #toggler переключет видимость
	   });
	});*/
	
	
	var all_trunk_in_draft = $('#draft_one div.trunk')
	var prev = 0
	for (var i = 0; i < all_trunk_in_draft.length; i++) 
				{
					//alert(Math.abs(all_trunk_in_draft[i].getBoundingClientRect().left));
					if (Math.abs(all_trunk_in_draft[i].getBoundingClientRect().left) > prev)
						{
							prev = Math.abs(all_trunk_in_draft[i].getBoundingClientRect().left)
							//summ = summ + Math.abs(all_trunk_in_draft[i].getBoundingClientRect().left/2)
							
						}
		 
				}
	/*$('aside.side-left').attr('style','margin-left:'+ prev +'px;')	*/	
	//$('#start').attr('style','margin-left:'+ parseInt(prev+100) +'px;')	
	canvas_lines_write();
	tralala();
	activePlus();
	button_click();
	drag();
	check_par();
	});
/*
$('#add_draft').click(function(){
	tralala();
	reUp();
	drag();
	activePlus()
})
*/


function check_par(){
$(".box-empty").has(".trunk").find('.plus_canvas').css({top:"-50px" , position:'relative'})
$(".box-empty, .split_trident").each(function()
                  {
                      if($(this).children(".trunk").length == 0)
                      {
                          $(this).find('.plus_canvas').css('position','static');
                      }
					  else
					  {
						  $(this).droppable( "disable" );
					}
                  });

}


 
$(function() {
 $('#inside-table a').click(function() {
    var cab_id=$(this).attr('id');
    cabClick(cab_id)
});
function cabClick(cab_id) {
    if (cab_id != $('#inside-table a.active').attr('id') ) {
        $('#inside-table .tabs').removeClass('active');
        $('#'+cab_id).addClass('active');
        $('#con_' + cab_id).addClass('active');
		
    }    
}
	  });
 
 //draft tabs

$(function() {
 $('aside a').click(function() {
    var tab_id=$(this).attr('id');
    tabClick(tab_id)
});
function tabClick(tab_id) {

    if (tab_id != $('aside a.active').attr('id') ) {
        $('aside .tabs').removeClass('active');
        $('#'+tab_id).addClass('active');
		
        $('#don_' + tab_id).addClass('active');
		                       
	}    
}
	  });
 
 
 /*
 function redirect(a) {
	 if ( $(a).children().eq(1).css("visibility")=='visible' ) {
	  $(a).children().eq(1).css('visibility', 'hidden');
	  $(a).children().eq(2).css('visibility', 'hidden');
	  $(a).children().eq(2).children().each(function(){
			$(this).droppable( 'disable' );
		});
	  }
	  else {
	  $(a).children().eq(1).css('visibility', 'visible');
	  $(a).children().eq(2).css('visibility', 'visible');
	  $(a).children().eq(2).children().each(function(){
			$(this).droppable( 'enable' );
		});
	  }
	 }
 */
 
 //draft tabs finished
 function button_click(){
	 $(".d-wrapper .polaroid a").click(function(){
		 	if ( $(this).closest('div[class^="trunk"]').is('.ui-draggable-dragging') ) {
                  return;
            }
	
		 //alert($(this).closest('div[class^="trunk"]').attr('id').split('_')[0]);
			 var splitt = $(this).closest('div[class^="trunk"]').attr('id').split('_')
			 var type_of_element = splitt[0] + '_' + splitt[1];
			 //alert($(this).closest('div[class^="box-empty"]').attr('id'));
			 if (type_of_element=='time_range') {
					var time_id_js = splitt[2];
				 }
			else if (type_of_element=='call_number') {
					var call_number = splitt[2];
				 }
			else if (type_of_element=='number_list') {
					var edit_list = splitt[2];
				 }
			else if (type_of_element=='voice_menu') {
					var edit_menu = $(this).closest('div[class^="trunk"]').attr('id');
				 }
			else if (type_of_element=='call_list') {
					var edit_list = splitt[2];
				 }
			else if (type_of_element=='check_direction') {
					var edit_temp = splitt[2];
				 }
			//$("#click_element").show('fast');
			$("#fon").show('fast');
			$(".container_null").show('fast');
			$.ajax({
				type: "POST",
				url: "/account/constructor/createnewelement/"+type_of_element+"/"+$(this).closest('div[class^="box-empty"]').attr('id')+"/",
				cache: false,
				async: false,
				data: {number_id: $("#number_drag_id").val(), draft_flag: false, time_id: time_id_js, call_number_id: call_number, edit_list_id: edit_list, edit_menu_id: edit_menu, edit_temp_id: edit_temp},  
				success: function(html){
					try{
					$(".tab_container").html(html);
					}
					catch(e) {
						
					}
					
				}  
		});
		
		
		if (type_of_element=='voice_menu' || type_of_element=='fax_rec')
		{	
			$('#select_number').val(splitt[2]);
			$('#select_number').change();
		}
		else if (type_of_element=='call_list' || type_of_element=='number_list') 
		{
			$('#choice_list_id').val(splitt[2]);
			$('#choice_list_id').change();
		}
		else if (type_of_element=='voice_mail')
		{	
			$('#select_number').val(splitt[2]);
			$('#select_number').change();
		}
		else if (type_of_element=='waiting_list') 
		{
			$('#choice_list_id').val(splitt[2]);
			$('#choice_list_id').change();
		}
		
		}) //$(".d-wrapper .polaroid a").click end
	 
	 
	$("#save_but").click(function(){
    $(".container").fadeOut('slow');
	$("#fon").fadeOut('slow');
	get_ajax_new_scheme2();
  });
   $("#cancel").click(function(){
	$(".container_null").fadeOut('slow');
    $(".container").fadeOut('slow');
	$("#fon").fadeOut('slow');
  });
  $('#cross_close').click(function(){
	  alert('aaa');
	$(".container_null").fadeOut('slow');
    $(".container").fadeOut('slow');
	$("#fon").fadeOut('slow');
	window.location.reload(true);
	//window.location.href=window.location.href;
  });
  $('#fon').click(function(){
	$(".container_null").hide('fast');
    $(".container").hide('fast');
	$("#fon").hide('fast');
	window.location.reload(true);
  });

  
  $(".plus_canvas").click(function(){
    $("#parent_plus_id").val($(this).parent().attr('id'));
	$(".container").fadeIn('fast');
	$("#fon").fadeIn('fast');
  });
  }
 /*
 $(document).ready(function(){
	 button_click();
});



$(function(){
	 $("#cross_close").click(function(){
		$("#fon").fadeOut('slow');
		$(".container").fadeOut('slow');

})
})
/*
	$(".box-empty").click(function(){
    $("#fon").fadeIn('slow');
})

*/

 function activePlus(){
 $(function(){
 $('.plus_canvas').click(function(){
    $('.plus_canvas').removeClass('active_plus');
    $(this).addClass('active_plus');
});

}
 )
 }
  $(function(){
 $('a.tabs').click(function(){
    $('a.tabs').removeClass('active_tabs');
    $(this).addClass('active_tabs');
});


 })
 


function get_ajax_new_scheme2() {
// $(".inside_table").find("#con_tab1").css('background','red');

$.post(
  "/account/constructor/scheme_save/",
  {
   // param3: $('#start_drop').find('.active_plus').attr('id'),
    param1: $('.all_d').find('.active_tabs').attr('id'),
    param2: $('#start_drop').html(),
  },
  onAjaxSuccess
);
}
function onAjaxSuccess(data)
{
  // Здесь мы получаем данные, отправленные сервером и выводим их на экран.
/*
 $('#start_drop').children().remove();
 */
 /*
	$('#start_drop').append(data);
	*/
	/*
	tralala();
	*/
	
	$(function() {
	 $('#inside-table a').click(function() {
		var tab_id=$(this).attr('id');
		tabClick(tab_id)
	});
	function tabClick(tab_id) {
		if (tab_id != $('#inside-table a.active').attr('id') ) {
			$('#inside-table .tabs').removeClass('active');
			$('#'+tab_id).addClass('active');
			$('#con_' + tab_id).addClass('active');
		}    
	}
		  });
	alert("onAjaxSuccess");
	
	//button_click();
	drag();
	$(function(){
		$("#cross_close").click(function(){
			$("#fon").fadeOut('slow');
			$(".container").fadeOut('slow');
	
	})
	})
	
	
	 $(function(){
		 
	 $('.plus_canvas').click(function(){
		$('.plus_canvas').removeClass('active_plus');
		$(this).addClass('active_plus');
	});
	
	
	 })
	  $(function(){
	 $('a.tabs').click(function(){
		$('a.tabs').removeClass('active_tabs');
		$(this).addClass('active_tabs');
	});
	
	
	 })
	//draft tabs


 


	
	
	canvas_lines_write();
	
	
}



 
 
 
 
 
$(function() {
   $(".tab_content").hide(); //Hide all content
$("ul.tabs li:first").addClass("active").show(); //Activate first tab
$(".tab_content:first").show(); //Show first tab content
//On Click Event
$("ul.tabs li").click(function() {
    $("ul.tabs li").removeClass("active"); //Remove any "active" class
    $(this).addClass("active"); //Add "active" class to selected tab
    $(".tab_content").hide(); //Hide all tab content
    var activeTab = $(this).find("a").attr("href"); //Find the rel attribute value to identify the active tab + content
    $(activeTab).fadeIn(); //Fade in the active content
    return false;
	
});
  });
   
/*  
$(function() {
$( "div.objects" ).mouseover(function() {
$( "div.box-empty" ).addClass( "highlight-border", 1000, callback );
return false;
});
function callback() {
setTimeout(function() {
$( "div.box-empty" ).removeClass( "highlight-border" );
}, 4500 );
}
});*/
//
 /*
$(function(){
  $("div.trunk").click(function(){
    $(this).toggleClass("highlight-border");
  });
});
 */
//



//new
/*
$(function() {
$( "div.trunk" ).draggable({

revert:"invalid",cursor: "move"});

//
$( "div.box-empty").droppable({

accept: "div.objects",
accept:	"div.trunk",
activeClass: "ui-state-hover",
hoverClass: "ui-state-active",

drop: function( event, ui ) {
$( this )
.addClass( "ui-state-highlight" )
.find( "p" )
.html( "Dropped!" );
}
});

$( "#drop2").droppable({
accept: "div.trunk",

activeClass: "ui-state-hover",
hoverClass: "ui-state-active",
drop: function( event, ui ) {
$( this )
.addClass( "ui-state-highlight" )
.find( "p" )
.html( "Dropped2!" );     

}
});
});
 */
 //multi objects/*

 function tralala(){
			
			$('.container, #fon').hover(function(){
   $('body').css('overflow','hidden');  
},
                    function(){
   $('body').css('overflow','auto') 
});
			
			
			/*	$('#' + event.target.id).children().children().children().find('.box, .description').css('display','none')*/
				
			
			
			//trash bucket
			$('.delete').bind('DOMNodeInserted', function(event) {
					$("#fon").fadeIn('fast');
					if ((event.type == 'DOMNodeInserted') && (event.target.id)){
							
							//	$('#draft_one').find('.active').removeClass('active');
								
							$.ajax({
								type: "POST",
								url: "/account/constructor/deleteelement/",
								cache: false,
								async: false,
								data: {element: event.target.id},  
								success: function(html){
									window.location.reload(true)
								}  
							});
							
							$(this).children().remove();
							
							//if((event.target.id).attr('class') ==  )$("#draft_name a:first").trigger("click")
								
								
					} 
					});
			
			
			
			//trash bucket finished
			// show del panel
			function showPanel(){
			
			$('.objects').dblclick(function(){
				$(this).find('.icon_action').toggleClass('show_del');
			
			})
			//show del panel finished
			
			
			//delete by click
			$('.del').click(function(){
				$(this).parent().parent().parent().parent().remove();
			
			});
			
			$('.replace').click(function(){
				alert($(this).parent().parent().parent().parent().attr('id'));
				
			})
			//delete by click finished
				}
			// append new elem for side-left by plus-click
			
			
			
			
			
			
			
			
			//add_el_button
			
		//	$('#add_el_button').click(function(){
			//	$('#li_waiting_list').append('<div class="trunk ui-draggable" id="auto_redirect"><div class="tree"><div class="objects" id="new_call"><div class="box"><div class="polaroid"><a><img src="img/autoredirect.png"  width="40px" height="40px" alt="autoredirect"/></a></div></div><div class="description">Автоматическая переадресация</div></div><canvas  id="auto_redirect_canvas"  class="canvas"  width="308" height="70"></canvas><div  id="auto_redirect_drop" class="box-empty ui-droppable"><p></p><img  src="img/plus.png" width="16px" height="16px" alt="plus"/><br></div></div></div>').live();
			
			//})
			
			
			
			//add_el_button finished
			// append new el for side-left by plus-click finished
			
			// tool tips
			/*
			$('.side_name').mouseover(function(){
				 $(".side_spisok li a[title]").tooltip({ hide: { effect: "puff", duration: 300 },
			
				 });
			});
			$('.ui-tooltip').mouseover(function(){
				 $(this).remove();
			});
			*/
			/*podskazka
				$( ".side_name" ).hover(
						function() {
							$( '#podskaz' ).append( $( "<span>Перетяните элемент в схему</span>" ).css( 'border', '2px dashed #2884EA'));
							}, function() {
							$( '#podskaz' ).find( "span:last" ).remove();
									}
							);
				$( "#start" ).hover(
						function() {
						$( '#podskaz' ).append( $( "<span>Двойной щелчок для удаления/замены элемента</span>" ).css( 'border', '2px dashed #2884EA','width','70px') );
						},function() {
							$( '#podskaz' ).find( "span:last" ).remove();
									})
				*/ 
			//
			
			
			//for next plus 
		
			$('.draftdrop').bind('DOMNodeInserted', function(event) {
				if ((event.type == 'DOMNodeInserted') && (event.target.id)){
						showPanel();
						activePlus();
						if ((event.target.id == 'splitter') && ($('#' + event.target.id).parent().attr('id') == 'call_number_drop_19')){
							$.ajax({
											type: "POST",
											url: "/account/constructor/save",  // or just url: "/my-url/path/"
											data: {new_element: event.target.id, parent_new_element: $('#' + event.target.id).parent().attr('id'), number_id: $('#number_drag_id').val()},
											success: function(data) {
												window.location.reload(true)
												//window.location.href=window.location.href;
											},
											error: function(xhr, textStatus, errorThrown) {
												alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
											}
										});
						}
						
						else {
							var mass = event.target.id.split('_');
							$("#fon").fadeIn('fast');
							if (mass.length > 2) {
								$.ajax({
								type: "POST",
								url: "/account/constructor/deleteelement/",
								cache: false,
								async: false,
								data: {element: event.target.id, replace_element: 1},  
								success: function(html){
									$.ajax({
											type: "POST",
											url: "/account/constructor/save",  // or just url: "/my-url/path/"
											data: {new_element: mass.slice(0,3).join('_'), parent_new_element: $('#' + event.target.id).parent().attr('id'), number_id: $('#number_drag_id').val(), draft_flag: true, replace_element: html, replace_element_in_scheme: true},
											success: function(data) {
												
												last_id = $('#' + event.target.id).parent().attr('id')
												//window.location.hash = last_id
												window.location.reload(true)
												//window.location.href=window.location.href;
											},
											error: function(xhr, textStatus, errorThrown) {
												alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
											}
										});
									}  
								});
								} //if (mass.length > 2)
							else {
								$("#fon").fadeIn('slow');
								$(".container_null").fadeIn('slow');
								
										$.ajax({
											type: "POST",
											url: "/account/constructor/createnewelement/"+event.target.id+"/"+$('#' + event.target.id).parent().attr('id')+"/",
											cache: false,
											async: false,
											data: {number_id: $("#number_drag_id").val(), draft_flag: true},  
											success: function(html){
												$(".tab_container").html(html);
											}  
										});
								}
						}
					
					
				}
			})
		
		
			$('#start_drop').bind('DOMNodeInserted', function(event) {
					if ((event.type == 'DOMNodeInserted') && (event.target.id)){
						showPanel()
						activePlus();
						if (event.target.id == 'split_ter'){
							$.ajax({
											type: "POST",
											url: "/account/constructor/save",  // or just url: "/my-url/path/"
											data: {new_element: event.target.id, parent_new_element: $('#' + event.target.id).parent().attr('id'), number_id: $('#number_drag_id').val(), draft_flag: false},
											success: function(data) {
												window.location.reload(true)
												//window.location.href=window.location.href;
											},
											error: function(xhr, textStatus, errorThrown) {
												alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
											}
										});
						}
						
						else {
							var mass = event.target.id.split('_');
							if (mass.length > 2) {
								$("#fon").fadeIn('fast');
								$.ajax({
								type: "POST",
								url: "/account/constructor/deleteelement/",
								cache: false,
								async: false,
								data: {element: event.target.id, replace_element: 1},  
								success: function(html){
									
								$.ajax({
										type: "POST",
										url: "/account/constructor/save",  // or just url: "/my-url/path/"
										data: {new_element: mass.slice(0,3).join('_'), parent_new_element: $('#' + event.target.id).parent().attr('id'), number_id: $('#number_drag_id').val(), draft_flag: false, replace_element: html, replace_element_in_scheme: true},
										success: function(data) {
											
											last_id = $('#' + event.target.id).parent().attr('id')
											//window.location.hash = last_id
											window.location.reload(true)
											//window.location.href=window.location.href;
										},
										error: function(xhr, textStatus, errorThrown) {
											alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
										}
									});
									
								}  
							});
							
							
								}
							else {
								$("#fon").show('fast');
								$(".container_null").show('fast');
										$.ajax({
											type: "POST",
											url: "/account/constructor/createnewelement/"+event.target.id+"/"+$('#' + event.target.id).parent().attr('id')+"/",
											cache: false,
											async: false,
											data: {number_id: $("#number_drag_id").val(), draft_flag: false},  
											success: function(html){
												$(".tab_container").html(html);
											}  
										});
								
								}
						}
							/*
						$.ajax({
								type: "POST",
								url: "/account/constructor/getid",  // or just url: "/my-url/path/"
								data: {new_element: event.target.id},
								success: function(data) {
									event.target.id = data
									$('#' + event.target.id).parent().find('.plus_canvas',$(this)).css('top','-50px','position','relative'); 
									$('#' + event.target.id).find('.plus_canvas').css('top','0px','position','relative');	
									$('#' + event.target.id).parent().droppable('disable');
									$('#' + event.target.id).find('.hover').removeClass('hover');
									alert("111Congratulations! You scored: "+data);
										$.ajax({
											type: "POST",
											url: "/account/constructor/save",  // or just url: "/my-url/path/"
											data: {new_element: event.target.id, parent_new_element: $('#' + event.target.id).parent().attr('id'), number_id: $('#number_id').val()},
											success: function(data) {
												alert("Congratulations! You scored: "+data);
											},
											error: function(xhr, textStatus, errorThrown) {
												alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
											}
										});
								},
								error: function(xhr, textStatus, errorThrown) {
									alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
								}
							});			
						*/
				//////////////////ajax save all constructor
				//////////////////ajax save all constructor
					} 
					});
					
					
					
					$('#start_drop, #drop').bind('DOMNodeRemoved', function(event) {
					if ((event.type == 'DOMNodeRemoved') && (event.target.id)){
				//	alert('55')
						$('#' + event.target.id).parent().find('.plus_canvas').css('top','0px','position','relative').css('left','0px');
						//	alert('66')
						  $('#' + event.target.id).parent().droppable('enable');

						//alert('77')
					} 
					});
					// upgrade for single line pluses end here 
				
			$('#voice_menu_drop_first').bind('DOMNodeInserted', function(event) {
			if((event.type == 'DOMNodeInserted') && (event.target.id)){
				
				//alert($('#' + event.target.id).parent().find('.plus_canvas').attr('id'));
				
				$('#' + event.target.id).parent().parent().find('#img_1st').css('left','8px');
			
			
			}
			//upgrade for yes/no line pluses end here
			
			
			});
			$('#voice_menu_drop_2').bind('DOMNodeInserted', function(event) {
					if ((event.type == 'DOMNodeInserted') && (event.target.id)){
						
						$('#' + event.target.id).parent().parent().find('#img_2st').css('left','-8px')
						


						
					} 
					});		
					

	
			
					

			
			}

 

 


 
/*
$(function(){
  $("#li_voice_mail").click(function(){
   $(this).one().append('<div class="trunk  ui-draggable" id="waiting_list"> <div class="tree"><div class="objects" id="new_call"><div class="box"><div class="polaroid"><a><img src="/media/img/icons/shem/call_wait.png" width="40px" height="40px" alt="call_wait"></a></div></div><div class="description hover">Очередь</div><div class="icon_action hover"><a class="replace"></a><a class="del"></a></div></div>	</div><canvas id="waiting_list_canvas" class="canvas hover" width="308" height="70"></canvas><div id="waiting_list_drop" class="box-empty  ui-droppable hover"><p></p><img class="plus_canvas" id="waiting_list_plus" title="Добавить сюда новый узел" src="/media/img/icons/shem/plus.png" width="16px" height="16px" alt="plus"><br></div></div></script>');//.draggable();
		tralala();
		
		canvas_lines_write();
		
		drag();
		
		

  });
});/*
$(function(){
  $("23").click(function(){
   $('body').append('<div class="trunk ui-draggable" id="auto_redirect"><div class="tree"><div class="objects" id="new_call"><div class="box"><div class="polaroid"><a><img src="img/autoredirect.png"  width="40px" height="40px" alt="autoredirect"/></a></div></div><div class="description">Автоматическая переадресация</div></div><canvas  id="auto_redirect_canvas"  class="canvas"  width="308" height="70"></canvas><div  id="auto_redirect_drop" class="box-empty ui-droppable"><p></p><img  src="img/plus.png" width="16px" height="16px" alt="plus"/><br></div></div></div><script>$(document).ready(function(){ $("div.box-empty").droppable({activeClass: "highlight-border",hoverClass: "highlight-border",	drop: function(event, ui) {var $list = $(this);$helper = ui.helper;}, tolerance: "touch"}); $("div.trunk").draggable({activeClass: "highlight-border",hoverClass: "highlight-border",revert: "invalid",helper: "clone",cursor: "move",drag: function(event,ui){	var $helper = ui.helper;$($helper).addClass("");	} });function moveSelected($trunk,$selected){$($selected).each(function(){$(this).fadeOut(function(){$(this).appendTo($trunk).removeClass("selected").fadeIn();});			});		}function moveItem( $item,$list ) {$item.fadeOut(function() {$trunk.find(".trunk").hide();$trunk.appendTo( $list ).fadeIn();});	}});                                      </script>').draggable();

	

  });
});

/*
$("button").click(function () {
 
	  $("<div class='newbox'>I'm new box by appendTo</div>").append('body');
 
    });
*/
/*	
	  $('.stuff').append
('<div class="circle"><div class="tree"><div class="objects"><div class="box"><div></div class="polaroid"><a><img       src="img/autoredirect.png"  width="40px" height="40px" alt="autoredirect"/></a></div><div class="description">Автоматическая переадресация</div></div><canvas  id="auto_redirect_canvas"  class="canvas"  width="308" height="70"></canvas><div  id="auto_redirect_drop" class="box-empty"><p></p><img  src="img/plus.png" width="16px" height="16px" alt="plus"/><br></div></div></div>');
  }
*/
/*var originalTop = $('.').position().top;
   var originalLeft = $('').position().left;

   $('button').toggle(
         function() {
            $(".trunk").draggable({});},
         function() {
            $(".trunk").draggable('destroy');
            $('.trunk').position().top = originalTop;
            $('.trunk').position().left= originalLeft;
         });
 */

		
		
		