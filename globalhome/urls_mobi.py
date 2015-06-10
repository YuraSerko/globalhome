# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from fsmanage.admin import tester
from urls import *
admin.autodiscover()
from django.core.urlresolvers import reverse
reverse('account.views.login')

urlpatterns = patterns('hotspot.views',
#  url(r'^statistic/$', 'hotspot_statistic', name='hotspot_statistic'),
    url(r"^hotspot/ajax_iformation/$", "ajax_hotspot_information", name="ajax_hotspot_information"),
    # url(r"^hotspot/ajax_hyper/$", "ajax_hyper", name="ajax_hyper"),
    url(r"^hotspot/ajax_review/$", "ajax_hotspot_review", name="ajax_hotspot_review"),
    url(r"^hotspot/n_a/$", "not_aval_func", name="not_aval_func"),
    url(r"^finance/currency/$", "hotspot_rate", name="hotspot_rate"),
    url(r'^$', 'hotspot_login', name='hotspot_login'),
    url(r"^news/$", "all_news", name="all_news"),
    url(r"^news/(?P<slug>[-\w]+)/$", "main_news", name="main_news"),
    url(r"^games/(?P<section>[-\w]+)/$", "view_games", name="view_games"),
    url(r"^administration/$", "view_administration", name="view_administration"),
    url(r"^weather/$", "weather", name="weather"),
    url(r"^finance/history/$", "finance_history", name="finance_history"),
    url(r"^weather/change$", "weather_change", name="weather_change"),
    url(r"^weather/region/(?P<region_id>\d+)/$", "weather_region", name="weather_region"),
    url(r"^nearby/(?P<org>[-\w]+)/$", 'orgs', name='orgs'),
    url(r"^hotspot/ajax_orgs_points/$", 'ajax_orgs_points', name='ajax_orgs_points'),
    url(r"^hotspot/ajax_orgs_points/search/$", 'ajax_orgs_points_search', name='ajax_orgs_points_search'),
    url(r"^hotspot/ajax_orgs_points/seach_by_single_name/$", 'ajax_orgs_points_search_by_name', name='ajax_orgs_points_search_by_name'),
    url(r'^content/article/(?P<slug>[-\w]+)/$', 'article_mobi_slug', name='article_mobi_slug'),
    url(r'^mail_reg/$', 'mail_reg', name='mail_reg'),
    url(r'^ajax_mail_reg/$', 'ajax_mail_reg', name='ajax_mail_reg'),
    url(r'^mail/$', 'mail', name='mail'),
    url(r'^ajax_mail_check_user/$', 'ajax_mail_check_user', name='ajax_mail_check_user'),


    url(r'^content/findoc/(?P<slug>[-\w]+)/$', 'findoc_mobi_slug', name='findoc_mobi_slug'),
    url(r"^ajax_get_org/(?P<org_id>\d+)/$", "ajax_get_org", name="ajax_get_org"),
    url(r"^ajax_user_chage_org_one/$" , 'ajax_user_chage_org_one', name='ajax_user_chage_org_one'),
    url(r"^ajax_user_chage_find_differnce/$", "ajax_user_chage_find_differnce", name="ajax_user_chage_find_differnce"),
    url(r"^films/(?P<genre>[-\w]+)/$", "video_films", name="video_films"),
    url(r"^films/$", "video_films", name="video_films"),
    url(r"^serials/$", "video_serials", name="video_serials"),
    url(r"^serials/(?P<genre>[-\w]+)/$", "video_serials", name="video_serials"),
    url(r"^video/(?P<name>[-\w]+)/$", "video_play", name="video_play"),
    url(r"^hotspot/bad_link/$", "bad_link", name="bad_link"),
    url(r"^count_rate/(?P<object_id>\d+)/(?P<score>\d+)/$", "count_rate", name="count_rate"),
   
  
   

    )
    
    
    
urlpatterns += patterns('job.views',
    # work
    url(r"^work_acount/resume/$", "work_resume", name="work_resume"),
    url(r"^work_acount/resume/add_edit/(?P<resume_id>\d+)/$", "work_resume_add_edit", name="work_resume_add_edit"),
    url(r"^work$", "work", name="work"),
    url(r"^work_acount/personal_data/$", 'work_perosanl_data', name='peronal_data'),
    url(r"^ajax_work_metro_city_change/$", 'ajax_work_metro_city_change', name='ajax_work_metro_city_change'),
    url(r"^work_delete_photo/$", 'work_delete_photo', name='work_delete_photo'),
    url(r"^work_acount/work_employer_data/$", 'work_employer_data', name='work_employer_data'),
    url(r"^work_acount/vacancy/$", "work_vacancy", name="work_vacancy"),
    url(r"^work_acount/vacancy/add_edit/(?P<vacancy_id>\d+)/$", "work_vacancy_add_edit", name="work_vacancy_add_edit"),
    url(r"^work_acount/work_resume_search$", 'work_resume_search', name="work_resume_search"),
    url(r"^work_account/work_resume_view/(?P<resume_id>\d+)/$", 'work_resume_view', name='work_resume_view'),
    url(r"^work_acount/work_vacancy_search$", 'work_vacancy_search', name="work_vacancy_search"),
    url(r"^work_account/work_vacancy_view/(?P<vacancy_id>\d+)/$", 'work_vacancy_view', name='work_vacancy_view'),
    url(r"^work_resume_ajax_publish/$", 'work_resume_ajax_publish', name='work_resume_ajax_publish'),
    url(r"work_vacancy_ajax_publish/$", 'work_vacancy_ajax_publish', name='work_vacancy_ajax_publish'),
    url(r"work_vacancy_ajax_delete/$", 'work_vacancy_ajax_delete', name='work_vacancy_ajax_delete'),
    url(r"work_resume_ajax_delete/$", 'work_resume_ajax_delete', name='work_resume_ajax_delete'),
    url(r"work/work_need_login/$", 'work_need_login', name='work_need_login'),
 )


urlpatterns += patterns('tvprogramma.views', 
    url(r"^tv_programma/$", "tv_forecast", name = "tv_forecast"),
    url(r"^tv_programma/(?P<date>\d{4}\-\d{2}\-\d{2})/$", "tv_forecast_date", name = "tv_forecast"),
    url(r"^tv_programma/(?P<channel_name>[-\w]+)/$", "tv_forecast_channel", name = "tv_forecast"),                
)






urlpatterns += patterns('tickets.views',
    url(r"^tickets/$", "ponominalu_tickets", name="ponominalu_tickets"),
    url(r"^tickets/grouptag/(?P<tag>[-\w]+)/(?P<region>[-\d]+)/$", "grouptag", name="grouptag"),
    url(r"^tickets/event/(?P<alias>[-\w]+)/(?P<region>[-\d]+)/$", "buy_ticket", name="buy_ticket"),
    #url(r"^event/(?P<alias>[-\w]+)/(?P<date>\d+.\d+.\d+)/(?P<time>\d+:\d+)/sector/(?P<sector_id>[-\w]+)/$", "sector_view", name="sector_view"),
    url(r"^tickets/venue/(?P<alias>[-\w]+)/(?P<region>[-\d]+)/$", "venue_view", name="venue_view"), 
)


urlpatterns += patterns('',

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^djangocontrib/jsi18n', 'django.views.i18n.javascript_catalog', name='djangocontrib_jsi18n'),
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.FILES_ROOT}),
    url(r'^ckeditor/', include('ckeditor.urls')),
    # (r'^comments/', include('django.contrib.comments.urls')),
)

###### ----------------urls.py ------------------

urlpatterns += patterns("payment.qiwi.views",
    url(r"^payment/card/qiwi/$", "payment_qiwi_card", name="qiwi_payment_card"),
    # url(r"^account/payment/card/qiwi/$", "account_payment_qiwi_card", name="account_qiwi_payment_card"),
    url(r"^account/payment/qiwi/$", "payment_qiwi", name="qiwi_payment"),
)

urlpatterns += patterns("payment.netpay.views",
    # url(r"^payment/card/qiwi/$", "payment_qiwi_card", name="qiwi_payment_card"),
    url(r"^payment/netpay/process/$", "payment_netpay_process", name="payment_netpay_process"),
    url(r"^account/payment/netpay/$", "payment_netpay", name="netpay_payment"),
)

urlpatterns += patterns("payment.webmoney.views",
    url(r"^payment/card/webmoney/$", "payment_wm_card_start", name="wm_payment_card_start"),
    url(r"^account/payment/webmoney/$", "payment_wm", name="wm_payment"),
    url(r"^account/payment/webmoney/success/$", "payment_wm_success", name="wm_payment_success"),
    url(r"^account/payment/webmoney/error/$", "payment_wm_error", name="wm_payment_error"),
    url(r"^account/payment/webmoney/process/$", "payment_wm_process", name="wm_payment_process"),
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns += patterns("payment.views",
    url(r"^payment/card/$", "payment_card", name="card_payment"),
    url(r"^account/payment/$", "payment_list", name="payment_list"),
    url(r"^account/payment/get_card/$", "account_payment_card", name="account_payment_card"),
    url(r"^account/payment/get_card/success/$", "account_payment_card_success", name="account_payment_card_success"),
    url(r"^account/payment/comepay/process/$", "payment_comepay_process", name="comepay_payment_process"),
    url(r'^account/payment/(?P<slug>[-\w]+)/$', 'article_cabinet_by_slug', name='article_cabinet_by_slug'),
    # url(r"^account/payment/cyberplat/process/$", "payment_cyberplat_process", name="cyberplat_payment_process"),


)
urlpatterns += patterns('devices.views',
#    url("^account/services/$", "services_list", name="services"),
    url("^account/invoices_and_payment/$", "invoices_and_payment", name="invoices_and_payment"),
    url("^account/advance_invoice/$", "advance_invoice", name="advance_invoice"),
#    url("^account/services/(?P<tel_number_id>\d+)/$", "service_add", name="service_add"),
    url("^account/invoices_and_payment/(?P<type_document>[-\w]+)/(?P<number_id>\d+)/$", "check_user_view", name="check_user_view"),
#    url("^account/services/delete/(?P<tel_number_id>\d+)/$", "service_del", name="service_del"),

    url("^account/write_offs_and_account_replenishment/$", "write_offs_and_account_replenishment", name="write_offs_and_account_replenishment"),
#    url(r"^change/", "t2"),
)
urlpatterns += patterns('data_centr.views',
#    url("^content/dedicated/send_zakaz/$", "dedicated_zakaz", name="dedicated_zakaz"),
    url("^account/rack/send_zakaz/$", "rack_zakaz", name="rack_zakaz"),
    url("^content/main_rack/send_zakaz/$", "main_rack_zakaz", name="main_rack_zakaz"),
#    url("^account/colocation/send_zakaz/$", "colocation_zakaz", name="colocation_zakaz"),
    url("^colocation/change_count_ip/(?P<count_ip>\d+)/$", "ajax_colocation_change_count_ip", name="ajax_colocation_change_count_ip"),
    url("^content/main_colocation/send_zakaz/$", "main_colocation_zakaz", name="main_colocation_zakaz"),
    url("^content/vds/$", "vds", name="vds"),
    url("^account/priority_of_services/$", "priority_of_services", name="priority_of_services"),
#    url("^content/vds/send_zakaz_256/$", "vds256_zakaz", name="vds256_zakaz"),
#    url("^content/vds/send_zakaz_512/$", "vds512_zakaz", name="vds512_zakaz"),
#    url("^content/vds/send_zakaz_1024/$", "vds1024_zakaz", name="vds1024_zakaz"),
#    url("^content/vds/send_zakaz_2048/$", "vds2048_zakaz", name="vds2048_zakaz"),
#    url("^content/vds/send_zakaz_3072/$", "vds3072_zakaz", name="vds3072_zakaz"),
#    url("^content/vds/send_zakaz_hand/$", "vds_zakaz_hand", name="vds_zakaz_hand"),


    url("^rack/cost_zakaz/$", "ajax_rack_cost_zakaz", name="ajax_rack_cost_zakaz"),
    url("^rack/change_ip/(?P<size_rack>[-\w]+)/$", "ajax_rack_change_ip", name="ajax_rack_change_ip"),
    url("^rack/change_socket/(?P<size_rack>[-\w]+)/$", "ajax_rack_change_socket", name="ajax_rack_change_socket"),
    url("^rack/change_electro/(?P<size_rack>[-\w]+)/$", "ajax_rack_change_electro", name="ajax_rack_change_electro"),

    url("^rack_step_auth/$", "rack_step_auth", name="rack_step_auth"),
    url("^rack_step_login/$", "rack_step_login", name="rack_step_login"),
    url("^rack_step_reg/$", "rack_step_reg", name="rack_step_reg"),

    url("^step_change_method_auth/$", "step_change_method_auth", name="step_change_method_auth"),
    url("^colocation_step_auth/$", "colocation_step_auth", name="colocation_step_auth"),
    url("^colocation_step_login/$", "colocation_step_login", name="colocation_step_login"),
    url("^colocation_step_reg/$", "colocation_step_reg", name="colocation_step_reg"),

    url("^colocation/cost_zakaz/$", "ajax_colocation_cost_zakaz", name="ajax_colocation_cost_zakaz"),
    url("^colocation/change_ff/(?P<type_ff>[-\w]+)/$", "ajax_colocation_change_form_factor", name="ajax_colocation_change_form_factor"),


    url("^dedicated/step_zakaz/(?P<account>[-\w]+)/(?P<server_id>\d+)/$", "ajax_dedicated_step_zakaz", name="ajax_dedicated_step_zakaz"),
    url("^dedicated/step_conf/(?P<account>[-\w]+)/$", "ajax_dedicated_step_conf", name="ajax_dedicated_step_conf"),
    url("^dedicated/step_auth/(?P<account>[-\w]+)/$", "ajax_dedicated_step_auth", name="ajax_dedicated_step_auth"),
    url("^dedicated/step_login/$", "ajax_dedicated_step_login", name="ajax_dedicated_step_login"),
    url("^dedicated/step_registration/$", "ajax_dedicated_step_registration", name="ajax_dedicated_step_registration"),
    url("^dedicated/change_type_inet/(?P<type_inet>[-\w]+)/$", "ajax_change_type_inet", name="ajax_change_type_inet"),
    url("^dedicated/cost_calculation/(?P<server_id>\d+)/$", "ajax_dedicated_cost_calculation", name="ajax_dedicated_cost_calculation"),


    url("^account/add_dedicated_final/$", "add_dedicated_final", name="add_dedicated_final"),
    url("^account/demands_dc/view_zayavka/(?P<zayavka_id>\d+)/$", "view_dc_zayavka", name="view_dc_zayavka"),
    url("^account/demands_dc/view_zakaz/(?P<zayavka_id>\d+)/$", "view_dc_zayavka", name="view_dc_zayavka"),
    url("^account/demands_dc/configuration/(?P<zakaz_id>\d+)/$", "ajax_dc_configuration", name="ajax_dc_configuration"),
    url("^account/demands_dc/apply_configuration/(?P<zakaz_id>\d+)/$", "apply_dc_configuration", name="apply_dc_configuration"),
)

urlpatterns = urlpatterns + patterns('helpdesk.views.account',
    url(r'^account/helpdesk/$', 'list_tickets', name='helpdesk_account_tickets'),  # list user's tickets
#    url(r'^account/helpdesk/add/$', 'create_ticket', name='helpdesk_account_tickets_add'),  # create new ticket
#    url(r'^account/helpdesk/(?P<ticket_id>[\d]+)/$', 'view_ticket', name='helpdesk_account_tickets_view'),  # change/post comment,
)

urlpatterns += patterns('account.views',
    url(r'^login/$', 'login', name='account_login'),
    url(r'^logout/$', 'logout', name='account_logout'),
#    url(r'^(?P<ref_code>[a-z0-9]{6})/registration/$', 'referral_registration', name='account_referral_registration'),
    url(r'^registration/$', 'registration', name='account_registration'),
    url(r'^registred/$', 'registration_completed', name='account_registration_completed'),
    url(r'^resetpassword/$', 'password_reset_request', name='account_password_reset_request'),
    url(r'^activation/(?P<action_key>[-_\d\w]+)/$', 'activation', name='account_activation'),
    url(r'^resend_activation_code/$', 'resend_activation_code', name='resend_activation_code'),
    url(r'^account/block/$', 'account_block', name='account_block'),

#    url("^account/service_choice/$", "service_choice", name="service_choice"),
    url("^account/demands_dc/$", "my_data_centr", name="my_data_centr"),
    url("^account/demands_dc/zayavka/(?P<hidden_id>\d+)/$", "del_zayavka", name="del_zayavka"),
    url("^account/demands_dc/zakaz/(?P<hidden_id>\d+)/$", "previously_del_zakaz", name="previously_del_zakaz"),
    url("^account/demands_dc/activation_zakaz/", "activation_zakaz", name="activation_zakaz"),
    url("^account/demands_dc/demands_dc_archive/", "demands_dc_archive", name="demands_dc_archive"),
    url('^account/$', 'account', name='account_profile'),
    url('^account/profile/$', 'account_profile_edit', name='account_profile_edit'),
    url("^account/data_centr/$", "account_data_centr", name="account_data_centr"),
    url("^account/rack/$", "account_rack", name="account_rack"),
    url("^account/colocation/$", "account_colocation", name="account_colocation"),
    url("^account/dedicated/$", "account_dedicated", name="account_dedicated"),
    url("^account/vds/$", "account_vds", name="account_vds"),
    url("^account/hosting/$", "account_hosting", name="account_hosting"),
    url("^account/communication_links/$", "account_communication_links", name="account_communication_links"),

    url('^account/changepassword/$', 'account_change_password', name='account_change_password'),
#    url('^account/balance/$', 'account_balance', name='account_balance'),
#    url('^account/fax/$', 'account_fax', name='account_fax'),
#    url('^account/fax/dajax/$', 'fax_dajax', name='fax_dajax'),
    url("^content/complaint/$", "complaint_phone", name="complaint_phone"),
    url("^content/wish-complaint/$", "complaint_int", name="complaint_int"),
    url("^change_our_requisites/$", "change_our_requisites", name="change_our_requisites"),
    url("^account/user_reg_check_ajax/$", "user_reg_check_ajax", name="user_reg_check_ajax"),

    # url("^add_equipment_rent/$", "add_equipment_rent", name="add_equipment_rent"),
)

urlpatterns += patterns("findocs.views",
    url("^account/findocs/signed/$", "findocs_list_signed", name="signed_financial_documents_list"),
    url("^account/findocs/signed/(?P<signed_id>\d+)/$", "findocs_show_signed", name="show_signed_financial_document"),
    url("^account/findocs/applications/sign/(?P<app_id>\d+)/$", "findocs_application_sign", name="signing_application_to_financial_document"),
    url('^account/findocs/contract_cancellation/$', 'contract_cancellation', name='contract_cancellation'),
    url('^account/findocs/resigning_of_contracts/$', 'resigning_of_contracts', name='resigning_of_contracts'),
)

urlpatterns += patterns("",
    url(r'^account/obzvon/$', 'fs.views.obzvon', name="obzvon"),
    url(r'^account/obzvon/new/$', 'fs.views.obzvon_new', name="obzvon_new"),
    url(r'^account/obzvon/repeat/(?P<id_repeat>\d+)/$', 'fs.views.obzvon_repeat', name="obzvon_repeat"),
    url(r'^account/obzvon/edit/(?P<id_edit>\d+)/$', 'fs.views.obzvon_edit', name="obzvon_edit"),
    url(r'^account/obzvon/preold/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_preold', name="obzvon_preold"),
    url(r'^account/obzvon/preold/ajax/$', 'fs.views.obzvon_preold_ajax', name="obzvon_preold_ajax"),
    url(r'^account/obzvon/delete/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_delete', name="obzvon_delete"),

    url(r'^account/queue/$', 'fs.views.queue_list', name='queue_list'),
    url(r'^account/queue/create/$', 'fs.views.queue_create', name='queue_create'),
    url(r'^account/queue/edit/(?P<queue_id>\d+)/$', 'fs.views.queue_edit', name='queue_edit'),
    url(r'^account/queue/delete/(?P<queue_id>\d+)/$', 'fs.views.queue_delete', name='queue_delete'),
    url(r'^account/queue/agents/(?P<queue_id>\d+)/$', 'fs.views.queue_agents', name='queue_agents'),
)

urlpatterns += patterns('internet.views',
    url("^account/internet/vpn/$", "vpn_users", name="vpn_users"),
    url("^account/internet/vpn/add/$", "vpn_users_add", name="vpn_users_add"),
    url("^account/internet/vpn/edit/(?P<vpn_id>\d+)/$", "vpn_users_edit", name="vpn_users_edit"),
    url("^account/internet/vpn/delete/(?P<vpn_id>\d+)/$", "vpn_users_del", name="vpn_users_del"),
    url("^account/internet/vpn/deleting/(?P<vpn_id>\d+)/$", "vpn_users_deleting", name="vpn_users_deleting"),
)
######-----------urls.py-----------

####urls globalhome
urlpatterns += patterns('account.views',
    url("^account/service_choice/$", "service_choice", name="service_choice"),
    url('^account/balance/$', 'account_balance', name='account_balance'),
    url('^account/fax/stat/$', 'account_balancefax', name='account_balancefax'),
    url('^account/fax/$', 'account_fax', name='account_fax'),
    url('^account/fax/dajax/$', 'fax_dajax', name='fax_dajax'),

)



#=============================================================================================
urlpatterns += patterns('equipment_rent.views',
    url("^account/equipment_rent_list/$", "equipment_rent_list", name="equipment_rent_list"),
    url("^equipment_rent/step_zakaz/(?P<account>[-\w]+)/(?P<device_id>\d+)/$", "ajax_equipment_rent_step_zakaz", name="equipment_rent_step_zakaz"),
    url("^equipment_rent/step_auth/(?P<account>[-\w]+)/$", "ajax_equipment_rent_step_auth", name="ajax_equipment_rent_step_auth"),
    url("^equipment_rent/step_login/$", "ajax_equipment_rent_step_login", name="ajax_equipment_rent_step_login"),
    url("^equipment_rent/step_registration/$", "ajax_equipment_rent_step_registration", name="ajax_equipment_rent_step_registration"),
    url("^equipment_rent/change_cost/(?P<device_id>[-\w]+)/$", "ajax_change_device_type", name="ajax_change_device_type"),
    url("^equipment_rent/add_item/$", "ajax_add_item", name="ajax_add_item"),
    url("^equipment_rent/sign_doc/$", "equipment_rent_sign_doc", name="equipment_rent_sign_doc"),

    url("^account/equipment_rent_list/zakaz/(?P<hidden_id>\d+)/$", "equipment_rent_del_zakaz", name="equipment_rent_del_zakaz"),
    url("^account/add_equipment_rent/$", "add_equipment_rent", name="add_equipment_rent"),
    url("^account/equipment_rent_list/del_package/(?P<package_id>\d+)/$", "del_package", name="del_package"),
)
#=============================================================================================
# reviews.view
urlpatterns += patterns('reviews.views',
    url(r'^reviews/$', 'review_page', name='review_page'),
    url(r'^reviews/write_review/$', 'write_review_page', name='write_review_page'),
    url(r'^reviews/my_reviews/$', 'my_reviews_page', name='my_reviews_page'),
    url(r'^reviews/all_reviews/$', 'all_reviews_page', name='all_reviews_page'),
)


urlpatterns += patterns('devices.views',
    url(r"^change/", "t2", name="t2"),
)

urlpatterns += patterns('content.views',
    url("^content/sim_card/$", "sim_card", name="sim_card"),
    url("^content/webphone/$", "webphone", name="webphone"),
    url("^content/phone_service/$", "phone_service", name="phone_service"),
)

urlpatterns += patterns("telnumbers.views",
    url("^account/phones/$", "phones_list", name="account_phones_list"),
    url('^account/phones/(?P<tel_number_id>\d+)/$', 'account_phone_edit', name='account_phone_edit'),
    url("^account/phones/add/$", "account_phone_add", name="account_phone_add"),
    url('^account/phones/delete/(?P<tel_number_id>\d+)/$', 'account_phone_delete', name='account_phone_delete'),
    url('^account/phones/statistics/(?P<tel_number_id>\d+)/$', 'account_phone_statistics', name='account_phone_statistics'),
)

urlpatterns += patterns("externalnumbers.number800",
    url("^account/8800/$", "list", name="8800_list"),
    url("^account/8800/connect", "connect", name="8800_connect"),
    url("^account/8800/delete/$", "delete", name="8800_delete"),
    url("^account/8800/reserved_free/$", "reserved_free", name="8800_reserved_free"),
    url("^account/8800/reserved_connect/$", "reserved_connect", name="8800_reserved_connect"),
    url("^account/8800/action/(?P<number_id>\d+)/$", "number_action", name="8800_action"),
    url("^account/8800/pause/$", "pause", name="8800_pause"),
    url("^account/8800/pause_delete/$", "pause_delete", name="8800_pause_delete"),
    url("^account/8800/pause_connect/$", "pause_connect", name="8800_pause_connect"),
    url("^account/8800/edit/(?P<number_id>\d+)/$", "edit", name="8800_edit"),
    url("^8800add/$", "add", name="8800_add"),
    url("^8800auth/$", "authorization", name="8800_auth"),
    url("^8800reg/$", "registration", name="8800_reg"),
)

urlpatterns += patterns("telnumbers.views_groups",
    url("^account/phones_groups/$", "groups_list", name="account_phones_groups"),
    url("^account/phones_groups/add/$", "groups_group_add", name="groups_group_add"),
    url("^account/phones_groups/edit/(?P<group_id>\d+)/$", "groups_group_edit", name="group_edit"),
    url("^account/phones_groups/delete/(?P<group_id>\d+)/$", "groups_group_delete", name="group_delete"),
)

urlpatterns += patterns("externalnumbers.views",
    url("^account/localphones/$", "external_list", name="external_phones_list"),
    url("^account/localphones/add/$", "external_add", name="external_phone_add"),
    url("^account/localphones/edit/(?P<number_id>\d+)/$", "external_edit", name="external_phone_edit"),
    url("^account/localphones/delete/(?P<number_id>\d+)/$", "external_number_delete", name="external_phone_delete"),

    url("^homepage/localphones/$", "mng", name="mng"),
    url("^step_1/(?P<id_tarif>[-_\d\w]+)/(?P<icode>[-_\d\w]+)/$", "step_1", name="step_1"),
    url("^step_2_auth/$", "step_2_auth", name="step_2_auth"),
    url("^step_2_reg/$", "step_2_reg", name="step_2_reg"),
    url("^account/add_number_final/$", "add_number_final", name="add_number_final"),
    url("^hot_key/$", "hot_key", name="hot_key"),
)

urlpatterns += patterns('',
    url(r"^account/mytariffs/", "tariffs.views.show_my_tariffs", name="account_show_tariffs"),
    url(r"^change_billing_group/", "account.views.change_customers_billing_group"),
    url(r"^change_telzone_group/", "tariffs.views.change_telzone_group")
)

urlpatterns += patterns("billing.views",
    url(r"^billing/utils/select_columns/", "select_columns"),
    url(r"^billing/utils/select_columns1/", "select_columns1"),
)

urlpatterns += patterns("",
    url("^account/call_forwarding/", include("call_forwarding.urls")),
)

urlpatterns += patterns("",
    url(r'^account/myivr/$', 'fs.views.list_ivr', name="list_ivr"),
    url(r'^account/myivr/edit_ivr/(?P<ivr_id>\d+)/$', 'fs.views.ivr_edit', name="edit_ivr"),
    url(r'^account/myivr/delete_ivr/(?P<ivr_id>\d+)/$', 'fs.views.ivr_delete', name="delete_ivr"),
    url(r'^account/myivr/create_ivr/$', 'fs.views.create_ivr', name="create_ivr"),
    url(r'^account/myivr/checkivr/$', 'fs.views.ajax_check_ivr', name="check_ivr"),

)

urlpatterns += patterns("",
    url(r'^account/listen_file_transaction/(?P<number>\d+)/(?P<filename>.*)$', 'fs.views.listen_file_transaction', name='listen_file_transaction'),
    url(r'^account/listen_file/(?P<filename>.*)$', 'fs.views.listen_file', name="listen_file"),
    url(r'^account/delete_file/(?P<filename>.*)$', 'fs.views.delete_file', name="delete_file"),
    url(r'^account/listen_file_archive/(?P<filename>.*)$', 'fs.views.listen_file_archive', name="listen_file_archive"),
    url(r'^account/delete_file_archive/(?P<filename>.*)$', 'fs.views.delete_file_archive', name="delete_file_archive"),
)

urlpatterns += patterns("",
    url(r'^account/phones_list/$', 'fs.views.groups_list', name="groups_list"),
    url(r'^account/phones_list/add/$', 'fs.views.groups_list_add', name="groups_list_add"),
#    url(r'^account/phones_list/edit/(?P<id_list>\d+)/$', 'fs.views.groups_list_add', name="groups_list_edit"),
    url(r'^account/phones_list/delete/(?P<id_list>\d+)/$', 'fs.views.groups_list_delete', name='groups_list_delete'),
    url(r'^account/phones_list/fix/edit/(?P<id_list>\d+)/(?P<id_type>\d+)/$', 'fs.views.groups_list_fixedit', name='groups_list_fix_edit'),
)

urlpatterns += patterns("",
    url(r'^account/obzvon/$', 'fs.views.obzvon', name="obzvon"),
    url(r'^account/obzvon/new/$', 'fs.views.obzvon_new', name="obzvon_new"),
    url(r'^account/obzvon/repeat/(?P<id_repeat>\d+)/$', 'fs.views.obzvon_repeat', name="obzvon_repeat"),
    url(r'^account/obzvon/preold/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_preold', name="obzvon_preold"),
    url(r'^account/obzvon/preold/ajax/$', 'fs.views.obzvon_preold_ajax', name="obzvon_preold_ajax"),
    url(r'^account/obzvon/delete/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_delete', name="obzvon_delete"),
)

urlpatterns += patterns("",
    url("^account/record_talk/", include("fs.urls")),
)

urlpatterns += patterns("",
    url("^account/transfer_call/help", "fs.views.transfer_call_help", name="transfer_call_help"),
)

urlpatterns += patterns("",
    url('^account/record_talk/delete_rt/$', 'fs.views.delete_rt', name='fs.views.delete_rt'),
    url('^account/record_balance/$', 'fs.views.record_balance', name='fs.views.record_balance'),
)

urlpatterns += patterns("",
    url(r'^account/voice_mail/list_vm/$', 'fs.views.list_vm', name="list_vm"),
    url(r'^account/voice_mail/create_vm/$', 'fs.views.create_vm', name="create_vm"),
    url(r'^account/voice_mail/edit_vm/(?P<vm_id>\d+)/$', 'fs.views.create_vm', name="edit_vm"),
    url(r'^account/voice_mail/delete_vm/(?P<vm_id>\d+)/$', 'fs.views.delete_vm', name="delete_vm"),
)

urlpatterns += patterns("",
    url(r'^account/getfax/list_getfax/$', 'fs.views.list_getfax', name="list_getfax"),
    url(r'^account/getfax/create_getfax/$', 'fs.views.create_getfax', name="create_getfax"),
    url(r'^account/getfax/delete_getfax/(?P<getfax_id>\d+)/$', 'fs.views.delete_getfax', name="delete_getfax"),
    url(r'^account/getfax/edit_getfax/(?P<getfax_id>\d+)/$', 'fs.views.create_getfax', name="edit_getfax"),
    url(r'^account/getfax/check/$', 'fs.views.ajax_check', name="ajax_check"),
)

urlpatterns += patterns("",
    url(r'^account/gateway/$', 'fs.views.list_gateway', name="list_gateway"),
    url(r'^account/gateway/add/$', 'fs.views.add_gateway', name="add_gateway"),
    url(r'^account/gateway/edit/(?P<id_gateway>\d+)/$', 'fs.views.add_gateway', name="edit_gateway"),
    url(r'^account/gateway/delete/(?P<id_gateway>\d+)/$', 'fs.views.delete_gateway', name="delete_gateway"),
)

urlpatterns += patterns('',
    (r'^fs/online_calls/$', tester),
    # (r'^doc1/$', test_drop),
)

urlpatterns += patterns('internet.views',


    url("^account/internet/demands/$", "my_inet", name="my_inet"),
    url("^account/add_inet_final/$", "add_inet_final", name="add_inet_final"),
    url("^account/internet/demands/configuration/(?P<zakaz_id>\d+)/$", "ajax_inet_configuration", name="ajax_inet_configuration"),
    url("^account/internet/demands/apply_configuration/(?P<zakaz_id>\d+)/$", "apply_configuration", name="apply_configuration"),


    url("^account/internet/demands/view_zayavka/(?P<zayavka_id>\d+)/$", "view_inet_zayavka", name="view_inet_zayavka"),
    url("^account/internet/demands/view_zakaz/(?P<zayavka_id>\d+)/$", "view_inet_zayavka", name="view_inet_zayavka"),
    url("^account/internet/demands/zayavka/(?P<zayavka_id>\d+)/$", "del_zayavka", name="del_zayavka"),
    url("^account/internet/demands/activation/(?P<zayavka_id>\d+)/$", "activation_zayavka", name="activation_zayavka"),
    url("^account/internet/demands/zakaz/(?P<zakaz_id>\d+)/$", "internet_del_zakaz", name="internet_del_zakaz"),
    url("^account/internet/demands/create_zakaz_free_inet/$", "create_zakaz_free_inet", name="create_zakaz_free_inet"),

    url("^account/internet/choose_face/$", "account_show_internet", name="account_show_internet"),
    url("^account/internet/choose_face/legal_entity/$", "account_internet_legal_entity", name="account_internet_legal_entity"),
    url("^account/internet/choose_face/physical/$", "account_internet_physical", name="account_internet_legal_entity"),
    url("^account/internet/choose_face/cottage_settlement/$", "account_internet_cottage_settlement", name="account_internet_legal_entity"),

    url("^internet/$", "show_internet", name="internet"),
    url("^internet/cover_zone/$", "internet_cover_zone", name="internet_cover_zone"),
    url("^internet/legal_entity/$", "internet_legal_entity", name="internet_legal_entity"),
    url("^internet/individual/$", "internet_individual", name="internet_individual"),

    url("^internet/individual/coverage_map/$", "internet_individual_coverage_map", name="internet_individual_coverage_map"),
    url("^internet/indivdual/ajax_internet_indivdiual_points/$", "ajax_internet_indivdiual_points", name="ajax_internet_indivdiual_points"),

    url("^internet/cottage_settlement/$", "internet_cottage_settlement", name="internet_cottage_settlement"),
    url("^internet/change_tariff/(?P<type_face>[-\w]+)/$", "ajax_change_tariff", name="ajax_change_tariff"),
    url("^internet/change_city/(?P<type_face>[-\w]+)/$", "ajax_change_city", name="ajax_change_city"),
    url("^internet/change_street/(?P<type_face>[-\w]+)/$", "ajax_change_street", name="ajax_change_street"),
    url("^internet/step_zakaz/(?P<account>[-\w]+)/(?P<type_face>[-\w]+)/$", "ajax_step_zakaz", name="ajax_step_zakaz"),
    url("^internet/step_auth/(?P<account>[-\w]+)/(?P<type_face>[-\w]+)/$", "ajax_step_auth", name="ajax_step_auth"),
    url("^internet/step_login/$", "ajax_step_login", name="ajax_step_login"),
    url("^internet/step_registration/$", "ajax_step_registration", name="ajax_step_registration"),
    url("^internet/interactive_search/$", "ajax_interactive_search", name="ajax_interactive_search"),
    url("^internet/interactive_search_point/$", "ajax_interactive_search_point", name="ajax_interactive_search_point"),
    url("^internet/schedule_connection/$", "ajax_schedule_connection", name="ajax_schedule_connection"),
    url("^internet/interactive_search_point/(?P<per_id>\d{1})/$", "ajax_interactive_search_point", name="ajax_interactive_search_point"),
)

urlpatterns += patterns('hotspot.views',
    url(r"^account/payment/hotspot-card/$", "payment_hotspot", name="payment_hotspot"),
    url(r"^account/internet/hotspot/statistic/$", "hotspot_statistic", name="hotspot_statistic"),
)

urlpatterns += patterns('content.views',
#    url(r'^content/article/$', 'article_list', name='article_list'),
    url(r'^content/article/(?P<id>\d+)/$', 'article', name='article'),
    url(r'^content/article/(?P<slug>[-\w]+)/$', 'article_by_slug', name='article_by_slug'),
#    url(r'^content/article/raw/(?P<slug>[-\w]+)/$', "raw_article_by_slug"),
    url(r'^content/news/$', 'news_list', name='news_list'),
    url(r'^content/news/(?P<id>\d+)/$', 'news', name='news'),
    url("^content/data_centr/$", "data_centr", name="data_centr"),
    url("^content/payment/$", "payment", name="payment"),
    url("^content/type_service/$", "type_service", name="type_service"),
)


urlpatterns += patterns('data_centr.views',
    url("^content/colocation/$", "colocation", name="colocation"),

    url("^content/dedicated/$", "dedicated", name="dedicated"),
    url("^content/rack/$", "rack", name="rack"),
)
# ## end urls globalhome



