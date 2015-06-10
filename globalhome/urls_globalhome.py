# coding: utf-8
from urls import *

urlpatterns += patterns('account.views',
    url("^account/service_choice/$", "service_choice", name="service_choice"),
    url('^account/balance/$', 'account_balance', name='account_balance'),
    url('^account/fax/stat/$', 'account_balancefax', name='account_balancefax'),
    url('^account/fax/$', 'account_fax', name='account_fax'),
    url('^account/fax/dajax/$', 'fax_dajax', name='fax_dajax'),
    url('^account/change_warn_balance/$', 'func_change_warn_balance', name='func_change_warn_balance'),
    #url('^account_ajax_change_pas/$', 'account_ajax_change_pas', name = 'account_ajax_change_pas'),
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

urlpatterns += patterns('account.views',
    url("^account/constructor/$", "number_with_constructor", name="number_with_constructor"),
    url("^account/constructor/save$", "save_constructor", name="save_constructor"),
    # url("^account/constructor/getid$", "create_new_element", name="create_new_element"),
    url("^account/localphones/scheme/new/(?P<number_id>\d+)/$", "constructor", name="constructor"),
    url("^account/constructor/createnewelement/(?P<newelement>[-\w]+)/(?P<parent_newelement>[-\w]+)/$", "modal_window", name="modal_window"),
    url("^account/constructor/deleteelement/$", "delete_element", name="delete_element"),
    url("^account/constructor/checklist/(?P<list_id>\d+)/$", "checklist", name="checklist"),
    # url("^account/constructor/checkbwlist/(?P<list_id>\d+)/$", "checkbwlist", name="checkbwlist"),
    url("^account/constructor/checkwaitlist/(?P<list_id>\d+)/$", "check_waiting_list", name="check_waiting_list"),
    url("^account/constructor/checkfax/(?P<fax_id>\d+)/$", "checkfax", name="checkfax"),
    url("^account/constructor/checkivr/(?P<ivr_id>\d+)/$", "checkivr", name="checkivr"),
    url("^account/constructor/checkvoicemail/(?P<voicemail_id>\d+)/$", "checkvoicemail", name="checkvoicemail"),
    url("^account/constructor/getform/$", "getform", name="getform"),
    # url("^account/constructor/getwidth/$", "getwidth", name="getwidth"),
    url("^account/constructor/create_draft/$", "createDraft", name="createDraft"),
)

urlpatterns += patterns('devices.views',
    url(r"^change/$", "t2", name="t2"),
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
    url(r'^account/number_template/(?P<id_number>\d+)/$', 'fs.views.number_template', name="number_template"),
    url(r'^account/number_template/changetemplate/$', 'fs.views.changetemplate', name="changetemplate"),

)

urlpatterns += patterns("",
    url("^account/record_talk/", include("fs.urls")),
)

urlpatterns += patterns("",
    url("^account/transfer_call/help", "fs.views.transfer_call_help", name="transfer_call_help"),
    url("^account/transfer_call/sendsms", "fs.views.send_esemes", name="send_esemes"),
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
    url("^account/internet/demands/activation2/$", "ajax_update_zakaz", name="ajax_update_zakaz"),
    url("^account/internet/demands/zakaz/(?P<zakaz_id>\d+)/$", "internet_del_zakaz", name="internet_del_zakaz"),
    url("^account/internet/demands/create_zakaz_free_inet/$", "create_zakaz_free_inet", name="create_zakaz_free_inet"),

    url("^account/internet/choose_face/$", "account_show_internet", name="account_show_internet"),
    url("^account/internet/choose_face/legal_entity/$", "account_internet_legal_entity", name="account_internet_legal_entity"),
    url("^account/internet/choose_face/physical/$", "account_internet_physical", name="account_internet_legal_entity"),
    url("^account/internet/choose_face/cottage_settlement/$", "account_internet_cottage_settlement", name="account_internet_legal_entity"),

    url("^wifi/$", "show_wifi", name="wifi"),

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
    url(r'^content/findoc/(?P<slug>[-\w]+)/$', 'findoc_globalhome_slug', name='findoc_globalhome_slug'),
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

# ��� ����� ������� WI FI
urlpatterns += patterns("payment.views",
    url(r"^account/payment/get_card/$", "account_payment_card", name="account_payment_card"),
    url(r"^account/payment/get_card/success/$", "account_payment_card_success", name="account_payment_card_success"),
)
