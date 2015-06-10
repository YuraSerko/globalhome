
//alert($('#id_service_type option:selected').text());
//инициализируем qjuery

 $(document).ready(function(){
    if (window.location.pathname=='/admin/data_centr/zakazy/add/'){
      $('.field-server').parent().css('display', 'none');
   $('.field-id').css('display', 'none');
    $('.field-city').parent().removeClass('collapsed');
    $('.field-city').parent().css('display', 'none');
    $('.field-ip').css('display', 'none');
    $('.field-electricity').css('display', 'none');
    $('.field-count_of_units').css('display', 'none');
    $('.field-count_of_port').css('display', 'none');
    $('.field-socket').css('display', 'none');
    $('.field-count_ip').css('display', 'none');

$('#id_section_type').on('change', function() {
    
  if ($('#id_section_type option:selected').val()==2){
//alert("Дата-центр");
    $('.field-ext_numbers').parent().css('display', 'none');
    $('.field-city').parent().removeClass('collapsed');
    $('.field-city').parent().css('display', 'none');
    $('.field-server').parent().css('display', 'block');
    $('.field-ip').css('display', 'block');
    $('.field-electricity').css('display', 'block');
    $('.field-count_of_units').css('display', 'block');
    $('.field-count_of_port').css('display', 'block');
    $('.field-socket').css('display', 'block');
    $('.field-count_ip').css('display', 'block');
  }
   if ($('#id_section_type option:selected').val()==3){
    //alert("Интеренет");
    $('.field-ext_numbers').parent().css('display', 'none');
    $('.field-city').parent().addClass('collapsed');
    $('.field-city').parent().css('display', 'block');
    $('.field-server').parent().css('display', 'none');
    $('.field-ip').css('display', 'block');
    $('.field-electricity').css('display', 'none');
    $('.field-count_of_units').css('display', 'none');
    $('.field-count_of_port').css('display', 'none');
    $('.field-socket').css('display', 'none');
    
    
  }
   if ($('#id_section_type option:selected').val()==1){
    //alert("Телефония");
    $('.field-ext_numbers').parent().css('display', 'block');
    $('.field-city').parent().removeClass('collapsed');
    $('.field-city').parent().css('display', 'none');
    $('.field-server').parent().css('display', 'none');
    $('.field-ip').css('display', 'none');
    $('.field-electricity').css('display', 'none');
    $('.field-count_of_units').css('display', 'none');
    $('.field-count_of_port').css('display', 'none');
    $('.field-socket').css('display', 'none');
    $('.field-count_ip').css('display', 'none');
  }
});
}
});

 