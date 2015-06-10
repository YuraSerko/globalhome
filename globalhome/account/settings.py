# -*- coding=utf-8 -*-
"""
Settings for account module
"""
from django.utils.translation import ugettext_lazy as _

# User area menu
# (view_name, verbose)

PERSONAL_AREA_MENU = [
    ("account_profile", _(u"Profile")),
    ("helpdesk_account_tickets", _(u"Support")),
    ("homepage", _(u"View site")),

    # ("#", _(u"Call us<br>online")),
    ("slug payment_methods", _("Payment<br>methods")),

    ("account_logout", _(u"Logout")),
]


PERSONAL_AREA_MENU_CARD = [
    ("account_profile", _(u"Profile")),
    ("helpdesk_account_tickets", _(u"Support")),
    ("homepage", _(u"View site")),

    # ("#", _(u"Call us<br>online")),

    ("account_logout", _(u"Logout")),
]


PERSONAL_AREA_STAFF_MENU = [
    ("helpdesk_dashboard", _(u"Dashboard")),
    ("helpdesk_list", _(u"Support")),
    ("helpdesk_submit", _(u"Make query")),
    ("helpdesk_report_index", _(u"Statistics")),
    ("homepage", _(u"View site")),
    ("account_logout", _(u"Logout")),
]


PROFILE_MENU_JURIDICAL_GLOBALHOME = [
    ("account_phones_list", None, None),
    ("account_phones_groups", None, None),
    ("external_phones_list", None, None),
    ("account_show_tariffs", None, None),
    ("callforwarding_rules_list", None, None),
    # тут мои добавленные
    ("account_fax", None, None),
    ("list_getfax", None, None),
    ("list_ivr", None, None),
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("list_vm", None, None),
    ("transfer_call_help", None, None),
    ("vpn_users", None, None),
    ("list_record_talk_tariff", None, None),

    ("my_inet", None, None),
    ("account_show_internet", None, None),
]

PROFILE_MENU_JURIDICAL_GLOBALMOBI = [
    ("account_phones_list", None, None),
    ("account_phones_groups", None, None),
    ("external_phones_list", None, None),
    ("account_show_tariffs", None, None),
    ("callforwarding_rules_list", None, None),
    # тут мои добавленные
    ("account_fax", None, None),
    ("list_getfax", None, None),
    ("list_ivr", None, None),
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("list_vm", None, None),
    ("transfer_call_help", None, None),
    ("vpn_users", None, None),
    ("list_record_talk_tariff", None, None),

    ("my_inet", None, None),
    ("account_show_internet", None, None),
]

PROFILE_MENU_JURIDICAL_MOSCOWDATA = [
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("account_dedicated", None, None),
    ("account_rack", None, None),
    ("account_colocation", None, None),
    ("account_vds", None, None),
    ("account_hosting", None, None),
    ("account_communication_links", None, None),
    ("vpn_users", None, None),
]


PROFILE_MENU_PHISICAL_GLOBALHOME = [
    ("account_phones_list", None, None),
    ("account_phones_groups", None, None),
    ("external_phones_list", None, None),
    ("account_show_tariffs", None, None),
    ("callforwarding_rules_list", None, None),
    # тут мои добавленные
    ("account_fax", None, None),
    ("list_getfax", None, None),
    ("list_ivr", None, None),
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("list_vm", None, None),
    ("transfer_call_help", None, None),
    ("vpn_users", None, None),
    ("list_record_talk_tariff", None, None),
    ("my_inet", None, None),
    ("account_show_internet", None, None),
]

PROFILE_MENU_PHISICAL_GLOBALMOBI = [
    ("account_phones_list", None, None),
    ("account_phones_groups", None, None),
    ("external_phones_list", None, None),
    ("account_show_tariffs", None, None),
    ("callforwarding_rules_list", None, None),
    # тут мои добавленные
    ("account_fax", None, None),
    ("list_getfax", None, None),
    ("list_ivr", None, None),
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("list_vm", None, None),
    ("transfer_call_help", None, None),
    ("vpn_users", None, None),
    ("list_record_talk_tariff", None, None),
    ("my_inet", None, None),
    ("account_show_internet", None, None),
]

PROFILE_MENU_PHISICAL_MOSCOWDATA = [
    ("my_data_centr", None, None),
    ("demands_dc_archive", None, None),
    ("account_data_centr", None, None),
    ("account_profile", None, None),
    ("helpdesk_account_tickets", None, None),
    ("account_dedicated", None, None),
    ("account_rack", None, None),
    ("account_colocation", None, None),
    ("account_vds", None, None),
    ("account_hosting", None, None),
    ("account_communication_links", None, None),
    ("vpn_users", None, None),

]


PROFILE_MENU_CARD = [
    ("account_balance", _(u"Calls imformation"), {"class":"change_link"}),
    ("account_show_tariffs", _(u"My tariffs"), {"class":"phone_link"}),
    ("hotspot_statistic", None, None),
]
