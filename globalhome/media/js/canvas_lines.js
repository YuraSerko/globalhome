function canvas_lines_write(){
    var drawingCanvas = document.getElementById('smile');
    if(drawingCanvas && drawingCanvas.getContext) {
    
	
	// start_canvas
	var canvas = document.getElementById('start_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 3;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	
	//waiting list
	var canvas = document.getElementById('waiting_list_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 3;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//waiting_list_end
	//1
	var canvas = document.getElementById('call_number-canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 3;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('call_list_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('time_range_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('number_list_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	
	//2
	//1
	var canvas = document.getElementById('number_list_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('voice_mail_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('fax_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//1
	var canvas = document.getElementById('auto_redirect_canvas');
    var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 70);
	obCanvas.lineWidth = 3	
	
	
	obCanvas.shadowColor = '#888';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	//2
	//разделяющая линия
	
	var canvas = document.getElementById('voice_menu_canvas')
	var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(154, 0);
    obCanvas.lineTo(154, 57);
	obCanvas.lineWidth = 3		
	
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
	  
	//canvas image 
	function loadImages(sources, callback) {
        var images = {};
        var loadedImages = 0;
        var numImages = 0;
        // get num of sources
        for(var src in sources) {
          numImages++;
        }
        for(var src in sources) {
          images[src] = new Image();
          images[src].onload = function() {
            if(++loadedImages >= numImages) {
              callback(images);
            }
          };
          images[src].src = sources[src];
        }
      }
      var canvas = document.getElementById('voice_menu_canvas');
      var context = canvas.getContext('2d');

      var sources = {
		yesPlus: 'img/plus.png',
        noPlus: 'img/plus.png',
      };

      loadImages(sources, function(images) {
        context.drawImage(images.yesPlus, 205, 75, 16, 16);
        context.drawImage(images.noPlus, 75, 75, 16, 16);
      });
	  
	  
	  //continue yes-line plus
	
	  
	 
	  
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
	
	
	
	
	//continue yes line 
	var canvas = document.getElementById('yesline')
/*	var obCanvas = canvas.getContext('2d');
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'green';
    obCanvas.moveTo(60, 0);
    obCanvas.lineTo(60, 140);
	obCanvas.lineWidth = 3		
	
    
	
	
	
	obCanvas.shadowColor = '#999';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	
	
	
	
	
	
	//continue yes line 
	
	var canvas = document.getElementById('noline')
	
	var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 2;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(60, 0);
    obCanvas.lineTo(60, 140);
	obCanvas.lineWidth = 3		
	
    
	
	obCanvas.shadowColor = '#999';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
	
	
	//draft line 
	
	var canvas = document.getElementById('draftline')
	var obCanvas = canvas.getContext('2d');
    
    obCanvas.beginPath();
    obCanvas.lineWidth = 3;
    obCanvas.strokeStyle = 'white';
    obCanvas.moveTo(80, 0);
    obCanvas.lineTo(80, 140);
	obCanvas.lineWidth = 2		
	
    
	
	obCanvas.shadowColor = '#999';
    obCanvas.shadowBlur = 200;
    obCanvas.shadowOffsetX = 150;
    obCanvas.shadowOffsetY = 150;
    
	obCanvas.stroke();	
   */}
   
   
	
}

window.onload = function() {canvas_lines_write();}
