# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

AVAILABLE_COLUMNS_FOR_FSMANAGE = (
    # формат: ( показывать по умолчанию?, имя атрибута модели, видимое имя )
    (True, "scr_ip", _(u"src_ip")),#"Начало звонка"),
    (True, "get_answer_time", _(u"Answer time")),
    (True, "get_session_end", _(u"Call end")),#"Конец звонка"),
    (True, "billable_session_length_in_min", _(u"Session length<br>in minutes")),#"Длина сессии<br>в минутах"),
    (True, "billable_session_length", _(u"Session length<br>in seconds")),#"Длина сессии<br>в секундах"),
    (True, "caller_account_name", _(u"Caller<br>account")),#"Вызывающий<br>абонент"),
    (True, "called_account_name", _(u"Called<br>account")),#"Вызываемый<br>абонент"),
    (True, "caller_number", _(u"Caller<br>number")),#"Вызывающий<br>номер"),
    (True, "called_number", _(u"Called<br>number")),#"Вызываемый<br>номер"),
    (True, "tel_zone", _(u"Tel zone")),#"Телефонная<br>зона"),
    (True, "price_without_nds", _(u"Price<br>without VAT")),#"Цена<br>без НДС"),
    (True, "price_with_nds", _(u"Price<br>with VAT")),#"Цена<br>с НДС"),
    (True, "billable_summ_without_nds", _(u"Billable<br>summ<br>without VAT")),#"Списанная<br>сумма<br>без НДС"),
    (True, "billable_nds_summ", _(u"VAT<br>summ")),#"Сумма<br>НДС"),
    (True, "billable_summ_with_nds", _(u"Billable<br>summ<br>with VAT")),#"Списанная<br>сумма<br>с НДС"),
    (True, "read_codec", _(u"Codec")),
    (True, "disconnect_code", _(u"Disconnect<br>code")),
)


def get_selected_columns_for_fsmanage():
    s = ""
    for ac in AVAILABLE_COLUMNS_FOR_FSMANAGE:
        if ac[0]:
            s += "1"
        else:
            s += "0"
    return s


SELECTED_COLUMNS_DEFAULT2 = get_selected_columns_for_fsmanage()

def del_br(s):
    s = s.replace("<br>", " ").replace("<BR>", " ")
    return s


def generate_select_columns_form_html_for_fsmanage(selected):

    html = ""

    dd = SELECTED_COLUMNS_DEFAULT_FOR_FSSAMAGE
    if len(selected) < len(dd):
        for i in xrange(len(dd) - len(selected)):
            selected += "0"

    for i in xrange(len(selected)):
        if selected[i] == "1":
            checked = 'checked="checked"'
        else:
            checked = ""

        try:
            field = """
<p>
<input type="checkbox" name="col%(index)s" value="" id="col%(index)s_id" %(checked)s/>
<label for="col%(index)s_id">%(caption)s</label>
</p>
                """ % {
                "index": i,
                "checked": checked,
                "caption": del_br(AVAILABLE_COLUMNS_FOR_FSSAMAGE[i][2])
            }
        except:
            pass
        else:
            html += field


    return mark_safe(html)