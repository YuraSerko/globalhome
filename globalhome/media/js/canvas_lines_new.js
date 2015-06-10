function canvas_lines_write(){
	
	//$('.add_drop').click(function(){
		//$('<div></div>').appendTo('.box_empty')//здесь должен быть dropline,а в скобках drop
		
		
		
		//ширина канваса изначально
		//wid = $('#myCanvas').width()
		
		//увеличиваем текщую ширину на 20 процентво
		 
		//$('#myCanvas').attr('width',wid+200+'px')
		//rock()
		
		//увеличиваем ширину транк и дроплайна
		//$('.trunk').css('width',wid+200+'px')
		//$('.box_empty').css('width',wid*1.2)
		
		//переопределяем переменную после увеличения канваса
		
		//wid = $('#myCanvas').width()
		//определяем какой нужен марджин лефт(ширина канваса поделить на количество дропов в дроплайне плюс один)
		//marg = wid*0.7/($('.box_empty').children().length)+'px';
		//marg = 150+'px'
		//$('.box_empty').children().css('margin-left', marg)
		//$('.box_empty').css('width', marg+1+'%')
		
		//count=((marg)*($('.box_empty').children().length))
		
	
	
	//})

function drawArrow(fromx, fromy, tox, toy, type, num)
    {
        this.context.beginPath();
        this.context.moveTo(fromx, fromy);
        this.context.bezierCurveTo(fromx, (toy-fromy)/2, tox, (toy-fromy)/2, tox, toy);
        this.context.lineWidth = 2;
        this.context.strokeStyle = this.getColor(type, num);
        this.context.stroke();
    }
	
function draw()
    {
        var canvas = $('#arrows_canvas_'+this.id)[0];
        if (canvas) {
            canvas.width = this.width;
            canvas.height = this.height;
            if (canvas.getContext) {
                this.context = canvas.getContext('2d');
                for (var i=0; i<this.points.length; i++) {
                    this.drawArrow(this.left + this.nodeWidth/2, 0, this.points[i], this.height, this.type, i);
                }
            }

        }
    }

		function rock(){
			//var canvas = document.getElementById('voice_menu_canvas');
			//var context = canvas.getContext('2d');
			//var rectWidth = (canvas.offsetWidth)/4;
			//var rectHeight = 100;
			//var rectX = (canvas.offsetWidth)/2;
			//var rectY = (canvas.offsetHeight)/2;
			//var cornerRadius = 120;
			//context.lineWidth = 2;
			//context.strokeStyle = 'yellow';
			
		 
			//var statDotX = 20
			//var statDotY = 430
			function summ_prev_drop(canvas, count) {
					var summ_weight = 0;
					for (var n = 0; n <= count; n++) {
						var drop = $("#" + $('#'+canvas.id).next().children().get(n).id + "[class*='drop_']")
						if (n==count) {summ_weight+=parseInt((drop.attr('weight')*150)/2);}
						else {summ_weight+=parseInt(drop.attr('weight')*150);}
					}
					return summ_weight;
					
				}
			
			function diff(count_drop)
			{
				var allsumm=0;
				for (var n = 0; n < count_drop; n++) {
					var drop = $("#" + $('#'+canvas[i].id).next().children().get(n).id + "[class*='drop_']");
					
					allsumm += drop.attr('weight')*150;
					allsumm -= drop.attr('weight')*150;
				}
			}
			
			function init(){
				var canvas = document.getElementsByClassName('static_canvas')
				for (var i = 0; i < canvas.length; i++) {
					//$('#'+canvas[i].id).attr('style','left: -'+ 300 +'px; position:relative;')
					//$('#'+canvas[i].id).next().attr('style','left: -'+ 300 +'px; position:relative;')
					
					count_drop = $('#'+canvas[i].id).next().children().size();
					
					for (var n = 0; n < count_drop; n++) {
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(n).id + "[class*='drop_']");
						drop.attr('style','width:'+150*drop.attr('weight')+'px;')
						var fromx=canvas[i].width/2;
						var fromy=0;
						var tox=summ_prev_drop(canvas[i], n);
						var toy=canvas[i].height;
						canvas[i].getContext('2d').beginPath();
						canvas[i].getContext('2d').moveTo(fromx, fromy);
						canvas[i].getContext('2d').bezierCurveTo(fromx, (toy-fromy)/2, tox, (toy-fromy)/2, tox, toy);
						canvas[i].getContext('2d').lineWidth = 2;
						if (n==0) {canvas[i].getContext('2d').strokeStyle = 'green';}
						else {canvas[i].getContext('2d').strokeStyle = 'red';}
						canvas[i].getContext('2d').stroke();
						drop.children('img').attr('style', 'left:' + ((fromx-tox)/150)*50 + 'px;');
					}
				}
				
				
				var canvas = document.getElementsByClassName('call_number_canvas')
				for (var i = 0; i < canvas.length; i++) {
					count_drop = $('#'+canvas[i].id).next().children().size();
					
					for (var n = 0; n < count_drop; n++) {
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(n).id + "[class*='drop_']");
						drop.attr('style','width:'+150*drop.attr('weight')+'px;')
						var fromx=canvas[i].width/2;
						var fromy=0;
						var tox=summ_prev_drop(canvas[i], n);
						var toy=canvas[i].height;
						canvas[i].getContext('2d').beginPath();
						canvas[i].getContext('2d').moveTo(fromx, fromy);
						canvas[i].getContext('2d').bezierCurveTo(fromx, (toy-fromy)/2, tox, (toy-fromy)/2, tox, toy);
						canvas[i].getContext('2d').lineWidth = 2;
						canvas[i].getContext('2d').strokeStyle = 'purple';
						canvas[i].getContext('2d').stroke();
						drop.children('img').attr('style', 'left:' + ((fromx-tox)/150)*50 + 'px;');
					}
				}
				
				
				
				var canvas = document.getElementsByClassName('voice_static_canvas')
				
				for (var i = 0; i < canvas.length; i++) {
					
					count_drop = $('#'+canvas[i].id).next().children().size();
					
					for (var n = 0; n < count_drop; n++) {
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(n).id);
						drop.attr('style','width:'+150*drop.attr('weight')+'px;')
						var fromx=canvas[i].width/2;
						var fromy=0;
						var tox=summ_prev_drop(canvas[i], n);
						var toy=canvas[i].height;
						canvas[i].getContext('2d').beginPath();
						canvas[i].getContext('2d').moveTo(fromx, fromy);
						canvas[i].getContext('2d').bezierCurveTo(fromx, (toy-fromy)/2, tox, (toy-fromy)/2, tox, toy);
						canvas[i].getContext('2d').lineWidth = 2;
						canvas[i].getContext('2d').strokeStyle = 'yellow';
						canvas[i].getContext('2d').stroke();
						var node_height = drop.children('.node-caption').height();
						node_height = node_height-15+50;
						drop.children('img').attr('style', 'left:' + ((fromx-tox)/150)*50 + 'px;' + 'top:-' + node_height + 'px !important;');
					}
				}
				
				try{
				var start_drop_child = $("#" + $('#start_drop').children().get(1).id);
				$('#start_drop').attr('style','width:'+start_drop_child.width()+'px;');
				
				var canvasNode = document.getElementById('start_canvas')
				canvasNode.width=start_drop_child.width();
				}
				catch(e) {
					$('#start_drop').attr('style','width:'+150+'px;');
					var canvasNode = document.getElementById('start_canvas')
					canvasNode.width=150;
					}
				
				
					
				$('.draftdrop').each(function(i,elem) {
					try{
						var draft_one_child = $("#" + $(elem).children().get(1).id); 
						$(elem).attr('style','width:'+draft_one_child.width()+'px;');
						$(elem).parent().css("width",draft_one_child.width() + "px");
						//$('#start_draft').attr('style','width:'+draft_one_child.width()+'px;');
						var canvasNode = document.getElementById($(elem).siblings(".canvas").attr('id'));
						//alert($(elem).siblings(".canvas").attr('id'));
						canvasNode.width=draft_one_child.width();
						//$(elem).siblings(".canvas").css("width",draft_one_child.width() + "px");
					}
					catch(e) {
						$(elem).attr('style','width:'+150+'px;');
						$(elem).siblings(".canvas").css("width",150 + "px");
						
					}
				})
				
			}
			
			
			
			
			function init22(){
				
			var canvas = document.getElementsByClassName('voice_static_canvas')
				for (var i = 0; i < canvas.length; i++) {
					var context = canvas[i].getContext('2d')
					var startw = canvas[i].width
					var startwor = canvas[i].width
					var add = 0;
					var add_canvas = 400;
					if (startwor <= 450) {
						add = -275;
						add_canvas = 50;
						if (startwor == 450) {add_canvas = 200; add = -100;}
					}
					if (startwor > 900) {
						add = 200;
						add_canvas += 400;
					}
					//alert($('#'+canvas[i].id).parent().attr('id'));
					$('#'+canvas[i].id).parent().attr('style','width: '+startw+'px;')
					$('#'+canvas[i].id).attr('style','margin-left: -'+ add_canvas +'px;')
					$('#'+canvas[i].id).next().attr('style','left: -'+ parseInt(add_canvas/2) +'px;')
					count_drop = $('#'+canvas[i].id).next().children().size();
					//alert(count_drop);
					//var canvas = document.getElementById('voice_menu_canvas');
					//var context = canvas.getContext('2d');
					
					//var width = canvas.width;
					//var height = canvas.height;
					//ctx.moveTo(width/2, 0);
					//ctx.lineTo(width/2, height/2);
					context.lineWidth = 2;
					context.strokeStyle = 'yellow';
					//alert($('#'+canvas[i].id).find("div.trunk").length);
					//var context = canvas.getContext('2d')
					//no-line 2 
					//var add_for_right = 0;
					var summ_weight = 0;
					for (var n = count_drop-1; n >= 0; n--) {
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(n).id);
						summ_weight+=parseInt(drop.attr('weight'));
					}
					if (count_drop==summ_weight){
					var add_for_right=105*(Math.floor((summ_weight-1)/2));}
					else {
						var add_for_right=(105*(Math.floor((summ_weight)/2)));
						var last_drop = $("#" + $('#'+canvas[i].id).next().children().get(((count_drop/2 | 0)*2)-1).id)
						var first_drop = $("#" + $('#'+canvas[i].id).next().children().get(0).id);
						
						if (last_drop.attr('weight')>1 || first_drop.attr('weight')>1)
							{
								var add_for_right=(105*(Math.floor((summ_weight)/2)))-((Math.abs(last_drop.attr('weight')-first_drop.attr('weight'))*105)/2);
							}
						
						/*if (last_drop.attr('weight')>1)
						{
							var add_for_right=(105*(Math.floor((summ_weight)/2)))-52;
							//add_for_right=add_for_right-(105*last_drop.attr('weight'))/2;
							}
							
						if (first_drop.attr('weight')>1)
						{
							var add_for_right=(105*(Math.floor((summ_weight)/2)))-52;
							//add_for_right=add_for_right-(105*first_drop.attr('weight'))/2;
							}*/
						}
					if (count_drop % 2 == 1) {
							context.moveTo(154 + 100, 0);
							context.lineTo(154 + 100, 150);
							context.stroke();
							add_for_right += 50;
						}
					var ok = 0;
					var asdf = 0;
					var add_for_right_or = add_for_right;
					var beg = (count_drop/2 | 0);
					//add_for_right += (105*count_drop/2 | 0)-105;
					
					
					for (var k = 0; k <= beg-1; k++) {
						
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(k).id);
						
						var next_drop = $("#" + $('#'+canvas[i].id).next().children().get(k+1).id);
						
						try {var prev_drop = $("#" + $('#'+canvas[i].id).next().children().get(k-1).id);}
						catch (e) {}
						
						if (k>=0) {
							if(drop.attr('weight')>1) {
								//ok+=105*(drop.attr('weight')-1);
								//var ml=(100*(Math.floor((drop.attr('weight'))/2)))+60
								//drop.attr('style','margin-left:'+ ml +'px;')
								//asdf=(105*(Math.floor((drop.attr('weight'))/2)))+105;
								//asdf=105*drop.attr('weight');
								var ml=((100*(Math.floor((drop.attr('weight'))/2)))+60)+(100*(Math.floor((prev_drop.attr('weight'))/2)))
								drop.attr('style','margin-left:'+ ml +'px;')
								asdf=(105*(Math.floor((drop.attr('weight'))/2)))+105;
								try {
								if (prev_drop.attr('weight')>1) {asdf=asdf+(105*(Math.floor((prev_drop.attr('weight'))/2)))}
								}
								catch (e) {}
								}
							else
								{
									asdf=105;
									var ml=(100*(Math.floor((prev_drop.attr('weight'))/2)))+60
									drop.attr('style','margin-left:'+ ml +'px;')
									try {
									if (prev_drop.attr('weight')>1) {asdf=asdf+(105*(Math.floor((prev_drop.attr('weight'))/2)))}
									}
									catch (e) {}
									
								}
						}
						
						add_for_right = add_for_right - asdf;
						ok+=ok;
						var x1 = 348 + add - add_for_right;
						var y1 = 57;
						var x2 = 278 + add - add_for_right;
						var y2 = 5;
						var x3 = 303 + add - add_for_right;
						var y3 = 260;
						if (k==0) {drop.attr('style','margin-left:'+ parseInt(x3-28) +'px;')}
						//summ_weight+=parseInt(drop.attr('weight'));
						context.beginPath();
						context.moveTo(154+200+add, 0);
						context.bezierCurveTo(x1,y1,x2,y2,x3,y3);
						context.lineWidth = 2;
						context.strokeStyle = 'yellow';
						context.stroke();
						
						if (k==beg-1) {add_for_right = add_for_right - asdf;}
						//if (k==1) {add_for_right=105*(Math.round(summ_weight/2)-1); alert(add_for_right);}
						
					}
					add_for_right = 0-add_for_right;
					ok = 0;
					var prev = 0;
					var curr = 0;
					asdf = 0;
					if (count_drop==summ_weight){
					var add_for_right=105*(Math.floor((summ_weight-1)/2));}
					else {
						var add_for_right=(105*(Math.floor((summ_weight)/2)));
						var last_drop = $("#" + $('#'+canvas[i].id).next().children().get(((count_drop/2 | 0)*2)-1).id)
						var first_drop = $("#" + $('#'+canvas[i].id).next().children().get(0).id)
						
						
						if (last_drop.attr('weight')>1 || first_drop.attr('weight')>1)
							{
								if (last_drop.attr('weight')>1)
								{var lt_d = last_drop.attr('weight')/2;}
								else {var lt_d = last_drop.attr('weight');}
								
								if (first_drop.attr('weight')>1)
								{var ft_d = first_drop.attr('weight')/2;}
								else {var ft_d = first_drop.attr('weight');}
								
								var add_for_right=(105*(Math.floor((summ_weight)/2)))-((Math.abs(lt_d - ft_d)*105)/2);
							}
						
						
						/*if (last_drop.attr('weight')>1)
						{
							//var add_for_right=(105*(Math.floor((summ_weight)/2)))-52;
							add_for_right=add_for_right-(105*last_drop.attr('weight'))/4;
						}
						if (first_drop.attr('weight')>1)
						{
							var add_for_right=(105*(Math.floor((summ_weight)/2)))-52;
							//add_for_right=add_for_right-(105*first_drop.attr('weight'))/2;
							}*/
						}
					//alert((Math.floor((summ_weight)/2)));
					for (var j = ((count_drop/2 | 0)*2)-1; j >= beg ; j--) {
						var drop = $("#" + $('#'+canvas[i].id).next().children().get(j).id);
						var next_drop = $("#" + $('#'+canvas[i].id).next().children().get(j-1).id);
						
						try {var prev_drop = $("#" + $('#'+canvas[i].id).next().children().get(j+1).id);}
						catch (e) {}
						
						if (j<((count_drop/2 | 0)*2)-1) {
							if(drop.attr('weight')>1) {
								//ok+=105*(drop.attr('weight')-1);
								var ml=((100*(Math.floor((drop.attr('weight'))/2)))+60)+(100*(Math.floor((next_drop.attr('weight'))/2)))
								drop.attr('style','margin-left:'+ ml +'px;')
								asdf=(105*(Math.floor((drop.attr('weight'))/2)))+105;
								try {
								if (prev_drop.attr('weight')>1) {asdf=asdf+(105*(Math.floor((prev_drop.attr('weight'))/2)))}
								}
								catch (e) {}
								}
							else
								{
									//if (asdf>10005) {alert('ffff'); alert(asdf);}
									//else {asdf=105;}
									asdf=105;
									var ml=(100*(Math.floor((next_drop.attr('weight'))/2)))+60
									drop.attr('style','margin-left:'+ ml +'px;')
									try {
									if (prev_drop.attr('weight')>1) {asdf=asdf+(105*(Math.floor((prev_drop.attr('weight'))/2)))}
									}
									catch (e) {}
								}
						}
						else {
							if(drop.attr('weight')>1) {
								if (count_drop==3) {asdf=105/2;}
								
									var ml=((100*(Math.floor((drop.attr('weight'))/2)))+60)+(100*(Math.floor((next_drop.attr('weight'))/2)))
									drop.attr('style','margin-left:'+ ml +'px;')
									//asdf=(105*(Math.floor((drop.attr('weight'))/2)))+105;
								}
							else
								{	
									if (count_drop==3) {asdf=105/2;}
									
									var ml=(100*(Math.floor((next_drop.attr('weight'))/2)))+60
									drop.attr('style','margin-left:'+ ml +'px;')
								}
							}
						add_for_right = add_for_right - asdf;
						alert(add_for_right);
						//ok+=prev;
						if (add_for_right>=0) {
						var x1 = 360 + add + add_for_right;
						var y1 = 57;
						var x2 = 430 + add + add_for_right;
						var y2 = 5;
						var x3 = 405 + add + add_for_right;
						var y3 = 260;}
						else 
						{
							if (add_for_right>-105) 
								{
									context.moveTo(154 + 200+add, 0);
									context.lineTo(154 + 200+add, 150);
									context.stroke();
									continue;
								}
						var x1 = 348 + add + (add_for_right+105);
						var y1 = 57;
						var x2 = 278 + add + (add_for_right+105);
						var y2 = 5;
						var x3 = 303 + add + (add_for_right+105);
						var y3 = 260;
						}
						
						//if(drop.attr('weight')>1) {curr=105*(drop.attr('weight')-1); var ml=prev+curr+55; prev=105*(drop.attr('weight')-1); ok+=curr; drop.attr('style','margin-left:'+ ml +'px;');}
						
						context.beginPath();
						context.moveTo(154+200+add, 0);
						context.bezierCurveTo(x1,y1,x2,y2,x3,y3);
						context.lineWidth = 2;
						context.strokeStyle = 'yellow';
						context.stroke();
						//startw = startw - 300;
						//add_for_right += 105;
						//if (j==((count_drop/2 | 0)*2)-2) {add_for_right=105*(Math.round(summ_weight/2)-1); alert(add_for_right);}
					}
					
					
					//alert(k);
					}
					/*ctx.moveTo(370, 60);
					ctx.lineTo(371, 60);
					
					ctx.moveTo(340, 115);
					ctx.lineTo(341, 115);
					
					ctx.moveTo(80, 165);
					ctx.lineTo(81, 165);
					
					ctx.moveTo(90, 135);
					ctx.lineTo(91, 135);
					
					ctx.moveTo(95, 150);
					ctx.lineTo(96, 150);
					ctx.stroke();
					
					context.strokeStyle = 'red';
					ctx.moveTo(width/2, 0);
					context.bezierCurveTo(340,50,310,105,205,130);
					ctx.moveTo(205, 130);
					context.bezierCurveTo(80,165,90,135,95,150);
					//ctx.lineTo(position+25,height+20);
					ctx.stroke();
					position += rectSize + 150; 
					
					/*ctx.moveTo(width/2, 0);
					context.bezierCurveTo(250,357,320,305,245,560);
					//ctx.lineTo(position+25,height+20);
					ctx.stroke();*/
					 
					
					
					/*while(position < width) {
						//ctx.fillRect(position,height+10,rectSize,rectSize); //изменить на минус чтобы смотреть прямоуголник
						ctx.moveTo(width/2, 0);
						context.bezierCurveTo(position+50,57,position+120,5,position+95,260);
						//ctx.lineTo(position+25,height+20);
						ctx.stroke();
						position += rectSize + 150; 
						}*/
				}
			init()
	
	}
	rock()	
	
	var drawingCanvas = document.getElementById('start_canvas');
    if(drawingCanvas && drawingCanvas.getContext) {
    
	var canvas = document.getElementsByClassName('canvas')
	for (var i = 0; i < canvas.length; i++) {
		var obCanvas = canvas[i].getContext('2d')
    // do stuff
	obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'dodgerblue';
    obCanvas.moveTo(canvas[i].width/2, 0);
    obCanvas.lineTo(canvas[i].width/2, 70);
	obCanvas.lineWidth = 2	
	
	
	/*obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;*/
    
	obCanvas.stroke();	
}
	
	  /* Данная функция создаёт кроссбраузерный объект XMLHTTP */
  function getXmlHttp() {
    var xmlhttp;
    try {
      xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
    try {
      xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    } catch (E) {
      xmlhttp = false;
    }
    }
    if (!xmlhttp && typeof XMLHttpRequest!='undefined') {
      xmlhttp = new XMLHttpRequest();
    }
    return xmlhttp;
  }
  
  function getWidth(a) {
    var xmlhttp = getXmlHttp(); // Создаём объект XMLHTTP
	
    xmlhttp.open('POST', '/account/constructor/getwidth/', true); // Открываем асинхронное соединение
    xmlhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Отправляем кодировку
    xmlhttp.send("element_id=" + encodeURIComponent(a)); // Отправляем POST-запрос
    xmlhttp.onreadystatechange = function() { // Ждём ответа от сервера
      if (xmlhttp.readyState == 4) { // Ответ пришёл
        if(xmlhttp.status == 200) { // Сервер вернул код 200 (что хорошо)
          //document.getElementById("summa").innerHTML = xmlhttp.responseText; // Выводим ответ сервера
			alert(xmlhttp.responseText);
			//$('#con_' + a.id).html(xmlhttp.responseText);
		}
      }
    };
  }
	
	
	//STATIC CANVAS//
	/*var canvas = document.getElementsByClassName('static_canvas')
	for (var i = 0; i < canvas.length; i++) {
		var context = canvas[i].getContext('2d')
		var startw = canvas[i].width
		//no-line 2 
		add_for_right = 0
		if (startw==450) {
			$('#'+canvas[i].id).parent().children('.tree').children().attr('style','position:relative; right:70px;')
			canvas[i].style["position"] = "relative";
			canvas[i].style["right"] = "50px";
			add_for_right = 50;
			}
		else if (startw>450) 
			{
			canvas[i].style["position"] = "relative";
			canvas[i].style["right"] = "200px";
			add_for_right = 200;
			}
		addw = ((startw/150)-2)*30;
		var x1 = 200 + add_for_right;
		var y1 = 57;
		var x2 = 270 + add_for_right;
		var y2 = 5;
		var x3 = 245 + add_for_right;
		var y3 = 260;
		
		context.beginPath();
		context.moveTo(154 + add_for_right, 0);
		context.bezierCurveTo(x1+addw,y1,x2+addw,y2,x3+addw,y3);
		context.lineWidth = 2;
		context.strokeStyle = 'red';
		context.stroke();
		  
		//yes-line 1
		
		var x1 = 108 + add_for_right;
		var y1 = 57;
		var x2 = 38 + add_for_right;
		var y2 = 5;
		var x3 = 63 + add_for_right;
		var y3 = 260;
	
		context.beginPath();
		context.moveTo(154 + add_for_right, 0);
		context.bezierCurveTo(x1-addw,y1,x2-addw,y2,x3-addw,y3);
		context.lineWidth = 2;
		context.strokeStyle = 'green';
		context.stroke();
		}*/
	

	////////////////////////////////////////////////////////////
	
	
	
	
	//STATIC CANVAS fin//
	
	/*
	var canvas = document.getElementById('voice_menu_canvas')
	var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 57);
	obCanvas.lineWidth = 3	;	
	
	obCanvas.shadowColor = '#999';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//no line
	var canvas = document.getElementById('voice_menu_canvas');
    var context = canvas.getContext('2d');
    var rectWidth = 95;
    var rectHeight = 200;
    var rectX = 150;
    var rectY = 60;
    var cornerRadius = 90;	
	
    context.beginPath();
    context.moveTo(rectX, rectY);
    context.lineTo(rectX + rectWidth - cornerRadius, rectY);
    context.arcTo(rectX + rectWidth, rectY, rectX + rectWidth, rectY + cornerRadius, cornerRadius);
    context.lineTo(rectX + rectWidth, rectY + rectHeight);
    context.lineWidth = 3;
	context.strokeStyle = '#ff0000';
    context.stroke();
	  
	   //yes-line
	var canvas = document.getElementById('voice_menu_canvas');
    var context = canvas.getContext('2d');
    var rectWidth = 95;
    var rectHeight = 200;
    var rectX = 150;
    var rectY = 60;
    var cornerRadius = 90;

    context.beginPath();
    context.moveTo(rectX, rectY);
    context.lineTo(rectX + rectWidth - cornerRadius, rectY);
    context.arcTo(rectX - rectWidth, rectY, rectX - rectWidth, rectY + cornerRadius, cornerRadius);
    context.lineTo(rectX - rectWidth, rectY + rectHeight);
    context.lineWidth = 3;
    context.strokeStyle = 'green';
	context.stroke();
	
	
	
    
	obCanvas.stroke();	 
	
	*/
	
	
	//splitter//
	var canvas = document.getElementsByClassName('trident')
	for (var i = 0; i < canvas.length; i++) {
	var context = canvas[i].getContext('2d')
    var rectWidth = 150;
    var rectHeight = 200;
    var rectX = 290;
    var rectY = 60;
    var cornerRadius = 90;	
	
    context.beginPath();
    context.moveTo(rectX, rectY);
    context.lineTo(rectX + rectWidth - cornerRadius, rectY);
    context.arcTo(rectX + rectWidth, rectY, rectX + rectWidth, rectY + cornerRadius, cornerRadius);
    context.lineTo(rectX + rectWidth, rectY + rectHeight);
    context.lineWidth = 3;
	context.strokeStyle = 'black';
    context.stroke();
      
     
  
    var context = canvas[i].getContext('2d')
    var rectWidth = 190;
    var rectHeight = 200;
    var rectX = 250;
    var rectY = 60;
    var cornerRadius = 90;

    context.beginPath();
    context.moveTo(rectX, rectY);
    context.lineTo(rectX + rectWidth - cornerRadius, rectY);
    context.arcTo(rectX - rectWidth, rectY, rectX - rectWidth, rectY + cornerRadius, cornerRadius);
    context.lineTo(rectX - rectWidth, rectY + rectHeight);
    context.lineWidth = 3;
    context.strokeStyle = 'black';
	context.stroke();  
      
   
	var obCanvas = canvas[i].getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'black';
    obCanvas.moveTo(254, 0);
    obCanvas.lineTo(254, 57);
	obCanvas.lineWidth = 3	;	
	
	obCanvas.shadowColor = 'black';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	  
     
  
	var obCanvas = canvas[i].getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'black';
    obCanvas.moveTo(254, 57);
    obCanvas.lineTo(254, 190);
	obCanvas.lineWidth = 3	;	
	
	obCanvas.shadowColor = 'black';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
      
    
	}
	
	//splitter//
   }
   
   
	
}


 
 

 
  