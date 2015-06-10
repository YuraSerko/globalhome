


function drag(){
	// alert('beforesave_drag loaded')
					$("div.trunk, .drafter, div.trunk_splitter").draggable({
						activeClass: "highlight-border-hover",
						hoverClass: "highlight-border",
						helper: "original", 
						cursor: "move",
						revert: true,
						scroll: true,
						refreshPositions: true,
						delay: 150, //для предотвращения нежелательного перетаскивания элемента при случайном щелчке мыши можно еще distance в пикс
						start: function(event,ui){
							  $(this).data("startingScrollLeft",$('#dffdfd').scrollLeft());
							  $(this).data("startingScrollTop",$('#dffdfd').scrollTop());
							  //alert($('#dffdfd').attr('id'));
						   },
						drag: function(event,ui){
								 var st = parseInt($(this).data("startingScrollLeft"));
								 var stt = parseInt($(this).data("startingScrollTop"));
      							 ui.position.left += $('#dffdfd').scrollLeft() - st;
								  ui.position.top += $('#dffdfd').scrollTop() - stt;
									//$('#draft_one').css('overflowY', 'inherit'); 
									//$('#draft_one').css('overflowX', 'inherit'); 
									//$('#' + this.id).draggable('option', 'helper', 'clone');
									//alert(this.id);
									// var $helper = ui.helper;
									//console.log(this.id);
									//$($helper).find('canvas, .plus_canvas').css({"z-index":"999 !important","background":"red","position":"relative","left":"-9999px"});
									//$($helper).find('#new_call').css({"margin-left":"20px"});
									//$($helper).find('.trunk').css({"position":"relative",'width':'20px !important'});
									//$($helper).find('.objects').css({"width":"40px"});

								 }
					
					// $($helper).clone().one().appendTo('#drop');
						//alert('loh2');
						//alert($('#start_drop').html());
					//alert($(this).children().last().attr('id'));
				
					/*$("div.box-empty" )
					.toggleClass( "highlight-border" )*/
 
				/*	var $selected = $(".selected");	
					if($selected.length > 1){	
						$($helper).html($selected.length + " trunk");
					}									
				},
				stop:	function(event,ui){
					var $helper = ui.helper;
					$($helper).clone().one().appendTo('#li_waiting_list');
					*/
						
				});
				/*$("#start_smart").draggable('disable')*/
				$("div.nedrag").draggable( 'disable' )
				$("div.split_trident").droppable({
					activeClass: "highlight-border",
					hoverClass: "highlight-border-hover",
					accept: "div.trunk_splitter ",
					tolerance: "intersect",
					over: function(){
						//alert($(this).attr('class'));
						//console.log($(this).attr('class'))
						},
					
					});
			
			
			 	
				$("div.box-empty").droppable({
					activeClass: "highlight-border",
					hoverClass: "highlight-border-hover",
					accept:'div.trunk',
					tolerance: 'intersect',
					
					});
				$("div.call_drop").droppable({
					activeClass: "highlight-border",
					hoverClass: "highlight-border-hover",
					accept:'div.trunk_splitter',
					tolerance: 'intersect',
					
					});
						

					$( "div[class*='over_canvas']" ).droppable({
					activeClass: "highlight-border",
					hoverClass: "highlight-border-hover",
					accept:function(d) { 
								if( $('#start_drop').find('#'+d.attr('id')).hasClass("trunk") ) 
								{ 
								return false; 
								}
								else {return true;}
					},
						
					over: function(){
						//alert($(this).attr('class'));
						//console.log($(this).attr('class'))
						},
					tolerance: "intersect"
					});
					
					$('#save_draft').click(function(){
						alert($('.side-left').find('.active').children().html());			 
					})
		
					$(".trash").droppable({
						activeClass: "trash_bucket",
						hoverClass: "trash_bucket_hover",
						accept: "div.trunk, .drafter, .trunk_splitter",
						tolerance: "pointer"
					});
					
					/*FROM QUERYSCRIPT DRAG*/
						
			$("div.box-empty, div.split_trident").droppable({
				drop: function(event, ui) {
					var $list = $(this);
					$helper = ui.helper;
					
					var $selected = $(".selected");					
					if($selected.length > 1){						
						moveSelected($list,$selected);
					}else{
						moveItem(ui.draggable,$list);
					}										
				}, tolerance: "pointer"
			 });
			 
			
			
			$("div.call_drop").droppable({
				drop: function(event, ui) {
					var $list = $(this);
					$helper = ui.helper;
					
					var $selected = $(".selected");					
					if($selected.length > 1){						
						moveSelected($list,$selected);
					}else{
						moveItem(ui.draggable,$list);
					}										
				}, tolerance: "pointer"
			 });
			
			 
			 
			 
			 
			 $(".item").draggable({
				revert: "invalid",
				helper: "clone",
				cursor: "move",
				drag: function(event,ui){
					var $helper = ui.helper;
					$($helper).removeClass("selected");
					var $selected = $(".selected");	
					if($selected.length > 1){	
						$($helper).html($selected.length + " items");
					}										
				}
			 });
			
			function moveSelected($list,$selected){
				$($selected).each(function(){
					$(this).fadeOut(function(){
						$(this).appendTo($list).removeClass("selected").fadeIn();
					});					
				});				
			}
			
			function moveItem( $item,$list ) {
				$item.fadeOut(function() {
					$item.find(".item").remove();
					$item.appendTo( $list ).fadeIn();
				});
			}
			
			$(".item").click(function(){
				$(this).toggleClass("selected");
			});
					
					
					
				}
				//drag();
//alert('beforesave finish')