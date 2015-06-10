


$(function(){ 
		$('#id_status').parent().parent().parent().addClass('id_status')
		$('#id_status').focus(function(){$('#id_status').blur()})
		if($("#form-field-wrapper-email").hasClass('error'))
		{
			if($("#form-field-wrapper-username").hasClass('error'))
			{
				$("#id_status").css('top','-30px')
			}
			else{$("#id_status").css('top','-21px')}
		}

        })

function chen(back) {
      $("#id_status").fadeIn("700")
      $("#id_status").css("background", back)
      }
      
function check(){
  user=$("#id_email").val() //check email
  if(user.length>="3")
  var items = { user:$('#id_email').val(),
               }
  		$.ajax({
           url: "/account/user_reg_check_ajax/",
           type: "POST",
           data: items,
           cache: true,
		   async: true,
           success: function(items){ 
              if(items=='1'){
              	var iteam="url(/media/images/stop.png) no-repeat"
              	chen(iteam)}
              else {
              	var iteam="url(/media/images/ok.png) no-repeat"
              	chen(iteam)
                }
               }  
             });
       if(user.length<="2")
         $("#id_status").hide()
       if(user=="") 
          $("#id_status").fadeOut()
  }
$(function(){
  
  var input = document.getElementById('id_email')
  input.oninput = function() { check()}
 
})

function empty(){
$("#ajall").empty()
$("#showimage1").empty()

}

  function clear(){
      var user=$('#id_username').val()
      if(user!='')
	  $('#id_username').val('')
	  $("#id_status").hide()}
  
	  $(function(){
	  	  
	  $('.link-login').click(empty)
	  $('.link-login').click(clear)
	  $('.link-register').click(empty)
      $('.link-register').click(clear)
      
      
    
               })