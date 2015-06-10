var intervalID

$(function(){
if($("#higher").html() ==  null){$('.find').css('left', '-222px')}
else{document.login.username.focus();}
})

if('{{chapid}}'){
intervalID = setInterval(function(){if($('.ya-site-form__submit').html()!= null){
$('.ya-site-form__submit').attr('onClick','ya_butt()')
clearinter()
}},500)
} 
else{
if($.cookie('mac')){
intervalID = setInterval(function(){if($('.b-serp-item__title-link').html()!= null){
$('.b-serp-item__title-link').attr('onmousedown','check_window(event,this)')//'location.href+="#zakaz"')
clearinter()
}},500)

}
}




function clearinter(){
clearInterval(intervalID)
//alert('stop')
}

function get_information(type){
items ={identity: "{{ identity }}",
		mac : "{{ macesc }}",
		type : type	}

			
$.ajax({
           url: "/hotspot/ajax_iformation/",
           type: "POST",
           data:items,
           cache: false,
		   async: false,
           success: function(items){ 
           $(".yandex_search_result").html(items)
           
            }
})



}

function check_window(event,obj){
event.preventDefault();
var href = $(obj).attr('href')
window.location.hash = "#zakaz"
$('#log_submit').attr('onclick','check_form("' + href + '")')
$('#sendin').attr('action',$.cookie('linkloginonly'))
}
function check_form(new_dst){
var submit = true;
var title_error;	
if(submit){if($('#m_username').val() == ''){submit = false; title_error = 'Заполните Логин'}}
if(submit){if($('#m_password').val() == ''){submit = false; title_error = 'Заполните Пароль'}}

if(submit){Login_dop_form(new_dst)}
if(! submit ){$("#error_td").show().html(title_error)}


}


function doLogin() {
        document.sendin.username.value = document.login.username.value;
        document.sendin.password.value = hexMD5('{{chapid}}'  + document.login.password.value + '{{ chapchallenge }}');
        document.sendin.submit();
        return false;
        }
function Login_dop_form(new_dst) {
        document.sendin.username.value = document.login_1.username.value;
        document.sendin.password.value = hexMD5($.cookie('chapid') + document.login_1.password.value + $.cookie('chapchallenge'));
        
        document.sendin.dst.value = new_dst
        alert(document.sendin.dst.value)
        document.sendin.submit();
        clear_cookies();
        return false;
        }  
    
function yandex_map(block_id, adres_str, manuf_adr,org_name){ 
	
       myMap = new ymaps.Map (block_id, {
            center: [adres_str[0],adres_str[1]],
            zoom: 12,
            type: 'yandex#publicMap',
            behaviors: ["default", "scrollZoom"]
            
        });
        myMap.controls
        // Кнопка изменения масштаба.
        .add('zoomControl', { left: 5, top: 5 })
        // Список типов карты
        .add('typeSelector')
        // Стандартный набор кнопок
        .add('mapTools', { left: 35, top: 5 });
		 ymaps.route([adres_str, manuf_adr],{ mapStateAutoApply: true }).then(function (route) {
		 
        myMap.geoObjects.add(route);
        var points = route.getWayPoints(),
            lastPoint = points.getLength() - 1;
        points.options.set('preset', 'twirl#redStretchyIcon');
        points.get(lastPoint).properties.set('iconContent', 'Точка прибытия').set('balloonContent', org_name);
        points.get(0).properties.set('iconContent', 'Вы тут')
        var homeGeocoder = ymaps.geocode(adres_str);
		homeGeocoder.then(function (res) {
    	var homeballoon =  res.geoObjects.get(0).properties.get('name')
    	points.get(0).properties.set('balloonContent', homeballoon);
            
    })
																									        
    }, function (error) {
        alert('Возникла ошибка: ' + error.message);
    });
  
}

function show_map(cli_a, adres_str, manuf_adr){

if($(cli_a).parent().find("#ya_map").is(':visible')){
$(cli_a).parent().find("#ya_map").hide()
$(cli_a).parent().find("#ya_map").children().empty()
$(cli_a).val('Показать на карте')
}
else{
var block_id = $(cli_a).parent().find("#ya_map").children().attr("id")
var org_name =  $(cli_a).parent().find("H5").html()
$(cli_a).parent().find("#ya_map").html(yandex_map(block_id,adres_str,manuf_adr,org_name))
$(cli_a).parent().find("#ya_map").show()
$(cli_a).val('Скрыть карту')
}
}

function ya_butt(){
$.cookie('trial', '{{ trial }}')
$.cookie('mac', '{{ mac }}')
$.cookie('ip', '{{ ip }}')
$.cookie('username', '{{ username }}')
$.cookie('linklogin', '{{ linklogin }}')
$.cookie('linkorig', '{{ linkorig }}')
$.cookie('error', '{{ error }}')
$.cookie('chapid', '{{ chapid }}')
$.cookie('chapchallenge', '{{ chapchallenge }}')
$.cookie('linkloginonly', '{{ linkloginonly }}')
$.cookie('linkorigesc', '{{ linkorigesc }}')
$.cookie('identity', '{{ identity }}')
$.cookie('macesc', '{{ macesc }}')
$.cookie('error', '{{ error }}')

}

function clear_cookies(){
$.cookie('trial', '')
$.cookie('mac', '')
$.cookie('ip', '')
$.cookie('username', '')
$.cookie('linklogin', '')
$.cookie('linkorig', '')
$.cookie('error', '')
$.cookie('chapid', '')
$.cookie('chapchallenge', '')
$.cookie('linkloginonly', '')
$.cookie('linkorigesc', '')
$.cookie('identity', '')
$.cookie('macesc', '')
$.cookie('error', '')

}