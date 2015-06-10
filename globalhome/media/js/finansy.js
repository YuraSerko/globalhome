    
$(function() {
      // Datepicker
  $('.datepicker').datepicker({
    firstDay: 1 ,
    changeMonth: true,
        changeYear: true,
        showOtherMonths: true,
        showButtonPanel: true,
        closeText: 'Ок',
        currentText: 'Сегодня',
    dateFormat: 'dd.mm.yy',
    dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    monthNames: ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'],
    monthNamesShort: ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
  });
  
  id_date_from = $("#id_date_from").attr('value');
  id_date_to = $("#id_date_to").attr('value');
  $('#id_date_from').datepicker('setDate', id_date_from);
  $('#id_date_to').datepicker('setDate', id_date_to);

  
  

  });