# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from content.TemplateVars import Variable, VarValue
from models import TelZoneGroup, Tariff
import settings
from django.db import connections
from csv_parse_tariffs import tel_zone_is_mobile, make_stat_zone_name
from tariffs.models import TariffGroup
import datetime
from django.db import transaction

def GetVariables():
    result = []

    class TariffTableVar(VarValue):

        def getValue(self):
            self.mark_safe = True
            self.request = self.init_kwargs.get("request")
            # а вот тут мы уже формируем таблицы

            group = self.kwargs.get("group")
            if not group:
                if self.kwargs.get("default"):
                    # отображаем дефолтные тарифы
                    billing_group_id = 1
                else:
                    # отображаем пользовательские тарифы
                    billing_group_id = self.request.user.get_profile().billing_account.group_id
            else:
                billing_group_id = group.id
            var_slug = self.kwargs.get("var_slug")
            if not var_slug:
                raise Exception("Tariff variable have'nt var_slug kwarg!!!")
            try:
                query = """
                    SELECT
                        tel_zones.name, "tel_zones"."ru_RU", tel_price.price,
                        tel_price.start_date, tel_price.end_date

                        FROM tel_zone_groups

                        INNER JOIN tel_zones ON tel_zone_groups.id=tel_zones.group_id
                        INNER JOIN tel_price ON tel_price.tel_zone_id=tel_zones.id
                        WHERE tel_zone_groups.var_slug='%(var_slug)s'
                        AND tel_price.billing_group_id='%(billing_group_id)s'
                """

                cursor = connections[settings.BILLING_DB].cursor()
                cursor.execute(
                    query % (
                        { "var_slug": var_slug, "billing_group_id": billing_group_id, }
                    )
                )
            except Exception, e:
                print e


            tfs = []
            row = True
            table_data = {}
            while row:
                row = cursor.fetchone()
                if not row:
                    break

                t = Tariff()
                # смотри только не вызови тут где-то t.save() !!!!! ибо горе великое случится в сей  же час!!!!!
                t.localized_zone_name = row[1]
                t.tel_zone_name = row[1] or row[0]  # вот так локализуем
                no_nds = self.kwargs.get("no_nds")
                if no_nds:
                    t.price = round(float(row[2]) / 1.18, 2)
                else:
                    t.price = round(row[2], 2)
                t.start_date = row[3]
                t.end_date = row[4]
                if t.is_active_check(custom_date=self.request.GET['date'] if self.request.GET.has_key('date') else ''):
                    tfs.append(t)

                    if not tel_zone_is_mobile(t.tel_zone_name):
                        name = t.tel_zone_name
                        table_row = table_data.get(name)
                        if table_row:
                            table_data[name][0] = t.price
                        else:
                            table_data[name] = [t.price, None]
                    else:
                        name = make_stat_zone_name(t.tel_zone_name)
                        table_row = table_data.get(name)
                        if table_row:
                            table_data[name][1] = t.price
                        else:
                            table_data[name] = [None, t.price]

            transaction.commit_unless_managed(settings.BILLING_DB)
            table_keys = table_data.keys()[:]
            table_keys.sort()

            # всё, вот тут формируем нормальную HTML-таблицу!!!!!!!!!!!!!!!!!!
            s = ""

            for key in table_keys:
                if table_data[key][1] is None:
                    mob_price = unicode(table_data[key][0])
                else:
                    mob_price = unicode(table_data[key][1])
                s += "<tr>"
                s += "<td>" + key + "</td>"
                s += "<td>" + unicode(table_data[key][0]) + "</td>"
                s += "<td>" + mob_price + "</td>"
                s += "</tr>"

            if not s:
                s = "<tr><td>%s</td></tr>" % _(u"Missing tariffs data in database!").__unicode__()

            return s
    # создадим набор переменных, соответствующих каждой группе зон
    tz_groups = TelZoneGroup.objects.all()
    t_groups = TariffGroup.objects.all()
    transaction.commit_unless_managed(using=settings.BILLING_DB)
    for grp in tz_groups:

        for tg in t_groups:
            default_t = Variable(
                "Tariffs_%s_%s" % (tg.group_name, grp.var_slug),
                u"Тарифы '%s' для группы телефонных зон '%s'" % (tg.group_name, grp.name),
                TariffTableVar(
                    var_slug=grp.var_slug,
                    group=tg,
                    default=True,
                    no_nds=False,

                ),
            )
            default_t_no_nds = Variable(
                "Tariffs_%s_no_nds_%s" % (tg.group_name, grp.var_slug),
                u"Тарифы '%s' для группы телефонных зон '%s' без НДС" % (tg.group_name, grp.name),
                TariffTableVar(
                    var_slug=grp.var_slug,
                    group=tg,
                    default=True,
                    no_nds=True,


                ),
            )
            default_t_no_nds_with_date = Variable(
                "Tariffs_%s_no_nds_with_data_%s" % (tg.group_name, grp.var_slug),
                u"Тарифы '%s' для группы телефонных зон '%s' без НДС с указанной датой" % (tg.group_name, grp.name),
                TariffTableVar(
                    var_slug=grp.var_slug,
                    group=tg,
                    default=True,
                    no_nds=True,

                ),
            )
            result.append(default_t)
            result.append(default_t_no_nds)
            result.append(default_t_no_nds_with_date)

        user_t = Variable(
            "Tariffs_user_" + grp.var_slug,
            u"Пользовательские тарифы для группы телефонных зон '%s'" % grp.name,
            TariffTableVar(
                var_slug=grp.var_slug,
                default=False,
                no_nds=True,


            ),
        )
        result.append(user_t)

    return result








