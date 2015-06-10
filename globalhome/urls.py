# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from fsmanage.admin import tester
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^add_name_to_url/$', 'page.views.add_name_to_url', name='add_name_to_url'),
    url(r'^$', 'page.views.homepage', name='homepage'),
    url(r'^search/$', 'page.views.search', name='search'),
    url(r'^admin/page/sender/add/', 'page.views.send_msg'),
    url(r'^users/(?P<name_user>[-\w\ \.\@]+)/$', 'page.views.view_user', name='view_user'),
    url(r'^admin/users_statistic/', 'account.views.users_statistic', name='users_statistic'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangocontrib/jsi18n', 'django.views.i18n.javascript_catalog', name='djangocontrib_jsi18n'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.FILES_ROOT}),
    url(r'^fax/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.FAX_ROOT}),
#    url(r'^helpdesk/', include('helpdesk.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),

)


# account
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
    #url('^account/$', 'account', name='account_profile'), //orignal
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
    url('^account_ajax_change_pas/$', 'account_ajax_change_pas', name = 'account_ajax_change_pas'),
    # url("^add_equipment_rent/$", "add_equipment_rent", name="add_equipment_rent"),
)

# contracts
# urlpatterns += patterns('',
#    url(r"^account/contracts/", include("contracts.urls")),
# )
# cards
#===============================================================================
# urlpatterns += patterns("cards.views",
#    url('^activationcard/$', 'activationcard', name='activationcard'),
# #    url('^activationcard1/$', 'contact', name='contact'),
# )
#===============================================================================

# proba service_del
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

urlpatterns += patterns('content.views',
#    url("^hostel/$", "hostelinform", name="hostelinform"),
#    url("^content/(?P<number_id>\d+)/$", "check_view", name="check_view"),
#    url("^content_send_to_email/(?P<number_id>\d+)/$", "send_to_emai", name="send_to_emai"),
#    url("^content_receipt/$", "check_receipt", name="check_receipt"),
#    url("^content/type_service/$", "type_service", name="type_service"),
#    url("^content/data_centr/$", "data_centr", name="data_centr"),
#    url("^content/sim_card/$", "sim_card", name="sim_card"),
#    url("^content/webphone/$", "webphone", name="webphone"),
#    url("^content/phone_service/$", "phone_service", name="phone_service"),
#    url("^content/payment/$", "payment", name="payment"),

)

# phones
# urlpatterns += patterns("telnumbers.views",
#    url("^account/phones/$", "phones_list", name="account_phones_list"),
#    url('^account/phones/(?P<tel_number_id>\d+)/$', 'account_phone_edit', name='account_phone_edit'),
#    url("^account/phones/add/$", "account_phone_add", name="account_phone_add"),
#    url('^account/phones/delete/(?P<tel_number_id>\d+)/$', 'account_phone_delete', name='account_phone_delete'),
#    url('^account/phones/statistics/(?P<tel_number_id>\d+)/$', 'account_phone_statistics', name='account_phone_statistics'),
# )


# phones groups
# urlpatterns += patterns("telnumbers.views_groups",
#    url("^account/phones_groups/$", "groups_list", name="account_phones_groups"),
#    url("^account/phones_groups/add/$", "groups_group_add"),
#    url("^account/phones_groups/edit/(?P<group_id>\d+)/$", "groups_group_edit"),
#    url("^account/phones_groups/delete/(?P<group_id>\d+)/$", "groups_group_delete"),
# )

# external phones
# urlpatterns += patterns("externalnumbers.views",
#    url("^account/localphones/$", "external_list", name="external_phones_list"),
#    url("^account/localphones/add/$", "external_add", name="external_phone_add"),
#    url("^account/localphones/edit/(?P<number_id>\d+)/$", "external_edit", name="external_phone_edit"),
#    url("^account/localphones/delete/(?P<number_id>\d+)/$", "external_number_delete", name="external_phone_delete"),
#
#    url("^homepage/localphones/$", "mng", name="mng"),
#    url("^step_1/(?P<id_tarif>[-_\d\w]+)/(?P<icode>[-_\d\w]+)/$", "step_1", name="step_1"),
#    url("^step_2_auth/$", "step_2_auth", name="step_2_auth"),
#    url("^step_2_reg/$", "step_2_reg", name="step_2_reg"),
#    url("^account/add_number_final/$", "add_number_final", name="add_number_final"),
#    url("^hot_key/$", "hot_key", name="hot_key"),
# )

# findocs
urlpatterns += patterns("findocs.views",
    url("^account/findocs/signed/$", "findocs_list_signed", name="signed_financial_documents_list"),
    url("^account/findocs/signed/(?P<signed_id>\d+)/$", "findocs_show_signed", name="show_signed_financial_document"),
    url("^account/findocs/applications/sign/(?P<app_id>\d+)/$", "findocs_application_sign", name="signing_application_to_financial_document"),
    url('^account/findocs/contract_cancellation/$', 'contract_cancellation', name='contract_cancellation'),
    url('^account/findocs/resigning_of_contracts/$', 'resigning_of_contracts', name='resigning_of_contracts'),
)

# tariffs
# urlpatterns += patterns('',
#    url(r"^account/mytariffs/", "tariffs.views.show_my_tariffs", name="account_show_tariffs"),
#    url(r"^change_billing_group/", "account.views.change_customers_billing_group"),
#    url(r"^change_telzone_group/", "tariffs.views.change_telzone_group")
# )

# content_varset
urlpatterns += patterns("",
    url(r"^content_variables/(?P<varset_id>\d+)/$", "content_variables.views.show_vars"),
    url(r"^content_variables/show_many/$", "content_variables.views.show_many_vars"),
)

# billing
# urlpatterns += patterns("billing.views",
#    url(r"^billing/utils/select_columns/", "select_columns"),
#    url(r"^billing/utils/select_columns1/", "select_columns1"),
# )


# call forwarding
# urlpatterns += patterns("",
#    url("^account/call_forwarding/", include("call_forwarding.urls")),
# )

# ivr
# urlpatterns += patterns("",
#    url(r'^account/myivr/$', 'fs.views.list_ivr', name="list_ivr"),
#    url(r'^account/myivr/edit_ivr/(?P<ivr_id>\d+)/$', 'fs.views.ivr_edit'),
#    url(r'^account/myivr/delete_ivr/(?P<ivr_id>\d+)/$', 'fs.views.ivr_delete'),
#    url(r'^account/myivr/create_ivr/$', 'fs.views.create_ivr'),
#    url(r'^account/myivr/checkivr/$', 'fs.views.ajax_check_ivr'),
#
# )

# urlpatterns += patterns("",
#    url(r'^account/listen_file_transaction/(?P<number>\d+)/(?P<filename>.*)$', 'fs.views.listen_file_transaction', name='listen_file_transaction'),
#    url(r'^account/listen_file/(?P<filename>.*)$', 'fs.views.listen_file', name="listen_file"),
#    url(r'^account/delete_file/(?P<filename>.*)$', 'fs.views.delete_file', name="delete_file"),
#    url(r'^account/listen_file_archive/(?P<filename>.*)$', 'fs.views.listen_file_archive', name="listen_file_archive"),
#    url(r'^account/delete_file_archive/(?P<filename>.*)$', 'fs.views.delete_file_archive', name="delete_file_archive"),
# )

# list_numbers
# urlpatterns += patterns("",
#    url(r'^account/phones_list/$', 'fs.views.groups_list', name="groups_list"),
#    url(r'^account/phones_list/add/$', 'fs.views.groups_list_add', name="groups_list_add"),
#    url(r'^account/phones_list/edit/(?P<id_list>\d+)/$', 'fs.views.groups_list_add'),
#    url(r'^account/phones_list/delete/(?P<id_list>\d+)/$', 'fs.views.groups_list_delete'),
#    url(r'^account/phones_list/fix/edit/(?P<id_list>\d+)/(?P<id_type>\d+)/$', 'fs.views.groups_list_fixedit'),
# )

# obzvon
# urlpatterns += patterns("",
#    url(r'^account/obzvon/$', 'fs.views.obzvon', name="obzvon"),
#    url(r'^account/obzvon/new/$', 'fs.views.obzvon_new', name="obzvon_new"),
#    url(r'^account/obzvon/repeat/(?P<id_repeat>\d+)/$', 'fs.views.obzvon_repeat', name="obzvon_repeat"),
#    url(r'^account/obzvon/preold/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_preold', name="obzvon_preold"),
#    url(r'^account/obzvon/preold/ajax/$', 'fs.views.obzvon_preold_ajax', name="obzvon_preold_ajax"),
#    url(r'^account/obzvon/delete/(?P<id_obzvon>\d+)/$', 'fs.views.obzvon_delete', name="obzvon_delete"),
#
# )

# queue
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

# record talk
# urlpatterns += patterns("",
#    url("^account/record_talk/", include("fs.urls")),
# )

# transfer_call
# urlpatterns += patterns("",
#    url("^account/transfer_call/help", "fs.views.transfer_call_help", name="transfer_call_help"),
# )


# urlpatterns += patterns("",
#    url('^account/record_talk/delete_rt/$', 'fs.views.delete_rt', name='fs.views.delete_rt'),
#    url('^account/record_balance/$', 'fs.views.record_balance', name='fs.views.record_balance'),
# )

# voice_mail
# urlpatterns += patterns("",
#    url(r'^account/voice_mail/list_vm/$', 'fs.views.list_vm', name="list_vm"),
#    url(r'^account/voice_mail/create_vm/$', 'fs.views.create_vm'),
#    url(r'^account/voice_mail/edit_vm/(?P<vm_id>\d+)/$', 'fs.views.create_vm'),
#    url(r'^account/voice_mail/delete_vm/(?P<vm_id>\d+)/$', 'fs.views.delete_vm'),
# )

# get fax
# urlpatterns += patterns("",
#    url(r'^account/getfax/list_getfax/$', 'fs.views.list_getfax', name="list_getfax"),
#    url(r'^account/getfax/create_getfax/$', 'fs.views.create_getfax'),
#    url(r'^account/getfax/delete_getfax/(?P<getfax_id>\d+)/$', 'fs.views.delete_getfax'),
#    url(r'^account/getfax/edit_getfax/(?P<getfax_id>\d+)/$', 'fs.views.create_getfax'),
#    url(r'^account/getfax/check/$', 'fs.views.ajax_check'),
# )

# gateway
# urlpatterns += patterns("",
#    url(r'^account/gateway/$', 'fs.views.list_gateway', name="list_gateway"),
#    url(r'^account/gateway/add/$', 'fs.views.add_gateway'),
#    url(r'^account/gateway/edit/(?P<id_gateway>\d+)/$', 'fs.views.add_gateway'),
#    url(r'^account/gateway/delete/(?P<id_gateway>\d+)/$', 'fs.views.delete_gateway'),
# )

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

urlpatterns = urlpatterns + patterns('helpdesk.views.account',
    url(r'^account/helpdesk/$', 'list_tickets', name='helpdesk_account_tickets'),  # list user's tickets
#    url(r'^account/helpdesk/add/$', 'create_ticket', name='helpdesk_account_tickets_add'),  # create new ticket
#    url(r'^account/helpdesk/(?P<ticket_id>[\d]+)/$', 'view_ticket', name='helpdesk_account_tickets_view'),  # change/post comment,
)


# способы оплаты
urlpatterns += patterns("payment.views",
    url(r"^payment/card/$", "payment_card", name="card_payment"),
    url(r"^account/payment/$", "payment_list", name="payment_list"),
    url(r"^account/payment/comepay/process/$", "payment_comepay_process", name="comepay_payment_process"),
    # url(r"^account/payment/cyberplat/process/$", "payment_cyberplat_process", name="cyberplat_payment_process"),


)
urlpatterns += patterns("payment.qiwi.views",
    url(r"^payment/card/qiwi/$", "payment_qiwi_card", name="qiwi_payment_card"),
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


#mercahnt
urlpatterns += patterns("payment.webmoney.views",
    url(r"^payment/card/webmoney/$", "payment_wm_card_start", name="wm_payment_card_start"),
    url(r"^account/payment/webmoney/$", "payment_wm", name="wm_payment"),
    url(r"^account/payment/webmoney/success/$", "payment_wm_success", name="wm_payment_success"),
    url(r"^account/payment/webmoney/error/$", "payment_wm_error", name="wm_payment_error"),
    url(r"^account/payment/webmoney/process/$", "payment_wm_process", name="wm_payment_process"),
)


# ajax views
# urlpatterns += patterns("ajax_views.views",
#    url(r"^ajax/get_account_groups_and_numbers/$", "get_account_groups_and_numbers", name = "get_account_groups_and_numbers"),
# )
# ajax
# urlpatterns += patterns('',
#    (r'^fs/online_calls/$', tester),
#    # (r'^doc1/$', test_drop),
# )

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


urlpatterns += patterns('internet.views',
    url("^account/internet/vpn/$", "vpn_users", name="vpn_users"),
    url("^account/internet/vpn/add/$", "vpn_users_add", name="vpn_users_add"),
    url("^account/internet/vpn/edit/(?P<vpn_id>\d+)/$", "vpn_users_edit", name="vpn_users_edit"),
    url("^account/internet/vpn/delete/(?P<vpn_id>\d+)/$", "vpn_users_del", name="vpn_users_del"),
    url("^account/internet/vpn/deleting/(?P<vpn_id>\d+)/$", "vpn_users_deleting", name="vpn_users_deleting"),
)

# urlpatterns += patterns('internet.views',
#    url("^account/internet/vpn/$", "vpn_users", name="vpn_users"),
#    url("^account/internet/vpn/add/$", "vpn_users_add", name="vpn_users_add"),
#    url("^account/internet/vpn/edit/(?P<vpn_id>\d+)/$", "vpn_users_edit", name="vpn_users_edit"),
#    url("^account/internet/vpn/delete/(?P<vpn_id>\d+)/$", "vpn_users_del", name="vpn_users_del"),
#    url("^account/internet/vpn/deleting/(?P<vpn_id>\d+)/$", "vpn_users_deleting", name="vpn_users_deleting"),
#
#
#    url("^account/internet/demands/$", "my_inet", name="my_inet"),
#    url("^account/add_inet_final/$", "add_inet_final", name="add_inet_final"),
#    url("^account/internet/demands/configuration/(?P<zakaz_id>\d+)/$", "ajax_inet_configuration", name="ajax_inet_configuration"),
#    url("^account/internet/demands/apply_configuration/(?P<zakaz_id>\d+)/$", "apply_configuration", name="apply_configuration"),
#
#
#    url("^account/internet/demands/view_zayavka/(?P<zayavka_id>\d+)/$", "view_inet_zayavka", name="view_inet_zayavka"),
#    url("^account/internet/demands/view_zakaz/(?P<zayavka_id>\d+)/$", "view_inet_zayavka", name="view_inet_zayavka"),
#    url("^account/internet/demands/zayavka/(?P<zayavka_id>\d+)/$", "del_zayavka", name="del_zayavka"),
#    url("^account/internet/demands/activation/(?P<zayavka_id>\d+)/$", "activation_zayavka", name="activation_zayavka"),
#    url("^account/internet/demands/zakaz/(?P<zakaz_id>\d+)/$", "internet_del_zakaz", name="internet_del_zakaz"),
#
#    url("^account/internet/choose_face/$", "account_show_internet", name="account_show_internet"),
#    url("^account/internet/choose_face/legal_entity/$", "account_internet_legal_entity", name="account_internet_legal_entity"),
#    url("^account/internet/choose_face/physical/$", "account_internet_physical", name="account_internet_legal_entity"),
#    url("^account/internet/choose_face/cottage_settlement/$", "account_internet_cottage_settlement", name="account_internet_legal_entity"),
#
#    url("^internet/$", "show_internet", name="internet"),
#    url("^internet/cover_zone/$", "internet_cover_zone", name="internet_cover_zone"),
#    url("^internet/legal_entity/$", "internet_legal_entity", name="internet_legal_entity"),
#    url("^internet/individual/$", "internet_individual", name="internet_individual"),
#    url("^internet/cottage_settlement/$", "internet_cottage_settlement", name="internet_cottage_settlement"),
#    url("^internet/change_tariff/$", "ajax_change_tariff", name="ajax_change_tariff"),
#    url("^internet/change_city/(?P<type_face>[-\w]+)/$", "ajax_change_city", name="ajax_change_city"),
#    url("^internet/change_street/(?P<type_face>[-\w]+)/$", "ajax_change_street", name="ajax_change_street"),
#    url("^internet/step_zakaz/(?P<account>[-\w]+)/(?P<type_face>[-\w]+)/$", "ajax_step_zakaz", name="ajax_step_zakaz"),
#    url("^internet/step_auth/(?P<account>[-\w]+)/(?P<type_face>[-\w]+)/$", "ajax_step_auth", name="ajax_step_auth"),
#    url("^internet/step_login/$", "ajax_step_login", name="ajax_step_login"),
#    url("^internet/step_registration/$", "ajax_step_registration", name="ajax_step_registration"),
#    url("^internet/interactive_search/$", "ajax_interactive_search", name="ajax_interactive_search"),
#    url("^internet/interactive_search_point/$", "ajax_interactive_search_point", name="ajax_interactive_search_point"),
# )


# urlpatterns += patterns('hotspot.views',
#    url(r"^account/payment/hotspot-card/$", "payment_hotspot", name="payment_hotspot"),
#    url(r"^account/internet/hotspot/statistic/$", "hotspot_statistic", name="hotspot_statistic"),
# )

# urlpatterns += patterns('hotspot.views',
#    url(r"^account/payment/hotspot-card/$", "payment_hotspot", name="payment_hotspot"),
#    url(r"^account/internet/hotspot/statistic/$", "hotspot_statistic", name="hotspot_statistic"),
# )
