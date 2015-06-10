$(document).ready(function() {
	
	// Expand Panel
	$("#open").click(function(){
		$("div#panel").slideDown("slow");
	
	});	
	
	// Collapse Panel
	$("#close").click(function(){
		$("div#panel").slideUp("slow");	
	});		
	
	// Switch buttons from "Log In | Register" to "Close Panel" on click
	$("#toggle a").click(function () {
		$("#toggle a").toggle();
	});		
		
});

$(document).ready(function() {
  // Expand Panel
  $("#open2").click(function(){
    $("div#panel2").stop(true,true).slideDown("slow");
  }); 
  // Collapse Panel
  $("#close2").click(function(){
    $("div#panel2").stop(true,true).slideUp("slow"); 
  });   
  // Switch buttons from "Log In | Register" to "Close Panel" on click
  $("#toggle2 a").click(function () {
    $("#toggle2 a").toggle();
  });   
});

$(document).ready(function() {
  // Expand Panel
  $("#open3").click(function(){
    $("div#panel3").fadeIn(500);
  }); 
  // Collapse Panel
  $("#close3").click(function(){
    $("div#panel3").slideUp("slow"); 
  });   
  // Switch buttons from "Log In | Register" to "Close Panel" on click
  $("#toggle3 a").click(function () {
    $("#toggle3 a").toggle();
  });   
});
$(document).ready(function() {
  // Expand Panel
  $("#open4").click(function(){
    $("div#panel4").stop(true,true).fadeIn(500);
	$("div#panel5").stop(true,true).fadeOut (500);
	$("div#panel6").stop(true,true).fadeOut (500);
  }); 
  // Collapse Panel
  $("#close4").click(function(){
    $("div#panel4").stop(true,true).fadeOut (500);
  });   
  // Switch buttons from "Log In | Register" to "Close Panel" on click
  $("#toggle4 a").click(function () {
    $("#toggle4 a").toggle();
  });   
});
$(document).ready(function() {
  // Expand Panel
  $("#open5").click(function(){
    $("div#panel5").stop(true,true).fadeIn(500);
	$("div#panel4").stop(true,true).fadeOut (500);
	$("div#panel6").stop(true,true).fadeOut (500);
  }); 
  // Collapse Panel
  $("#close5").click(function(){
    $("div#panel5").stop(true,true).fadeOut (500);
  });   
  // Switch buttons from "Log In | Register" to "Close Panel" on click
  $("#toggle5 a").click(function () {
     $("#toggle5 a").toggle();
  });   
});

$(document).ready(function() {
  // Expand Panel
  $("#open6").click(function(){
    $("div#panel6").stop(true,true).fadeIn(500);
	$("div#panel4").stop(true,true).fadeOut (500);
	$("div#panel5").stop(true,true).fadeOut (500);
  }); 
  // Collapse Panel
  $("#close6").click(function(){
    $("div#panel6").stop(true,true).fadeOut (500);
  });   
  // Switch buttons from "Log In | Register" to "Close Panel" on click
  $("#toggle6 a").click(function () {
     $("#toggle6 a").toggle();
  });   
});