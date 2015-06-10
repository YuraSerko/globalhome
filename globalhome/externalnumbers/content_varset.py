# coding: utf-8
from findocs.models import FinDocSignApplication
from telnumbers.models import TelNumbersGroup
from externalnumbers.models import ExternalNumber, ExternalNumberTarif, Number800Payments, Number800Regiones, Number800TrafficTariff
from content.TemplateVars import Variable, VarValue
from externalnumbers.consts import REGIONS
from django.utils.translation import ugettext_lazy as _
from findocs import get_signed
from findocs.models import Package_on_connection_of_service
from prices.models import PricesGroup, Price
import log
from settings import BILLING_DB, GLOBALHOME_DB2
from django.db import connections, transaction
from django.contrib.auth.models import User
from data_centr.models import Tariff, Price_connection
from externalnumbers.consts import dc as add_on_service
from findocs.models import FinDocSigned
from externalnumbers.number800 import number_format

def GetVariables():

    class ExternalNumberVarValue(VarValue):
        def getValue(self):
            option = self.args[0]
            request = self.init_kwargs["request"]
            user = request.user
            profile = user.get_profile()
            bac = profile.billing_account
            app_id = self.init_kwargs["findocapp_id"]
            try:
                app = FinDocSignApplication.objects.get(id=app_id)
            except Exception, e:
                log.add("Exception 1 in %s.GetVariables.ExternalNumberVarValue: '%s'" % (__name__, e))
                return "<WAS EXCEPTION WHEN GETTING APPLICATION BY ID - in %s.GetVariables.ExternalNumberVarValue>" % __name__

            try:
                params_data = app.unpickle_params()
                numbers_count = len(params_data["localnumbers_add_nums_ids"])
                user_prices_group = bac.prices_group
                sum_pay = 0
                sum_abon = 0
                cur = connections[BILLING_DB].cursor()
                for nums in params_data["localnumbers_add_nums_ids"]:
                    cur.execute("SELECT tarif_group FROM external_numbers WHERE id=" + str(nums) + ";")
                    external_numbers = cur.fetchone()
                    cur.execute("SELECT price_add,price_abon FROM external_numbers_tarif WHERE id=" + str(external_numbers[0]) + ";")
                    external_numbers = cur.fetchone()

                    # получаем цены для номера
                    cur.execute("SELECT cost FROM billservice_addonservice WHERE id=" + str(external_numbers[0]) + ";")
                    numb_add = cur.fetchone()
                    cur.execute("SELECT cost FROM billservice_addonservice WHERE id=" + str(external_numbers[1]) + ";")
                    numb_abon = cur.fetchone()
                    sum_pay = sum_pay + numb_add[0]
                    sum_abon = sum_abon + numb_abon[0]
                try:
                    connect_price = float(sum_pay) - float(sum_pay) * 0.18
                    abon_price = float(sum_abon) - float(sum_abon) * 0.18
                except Exception, e:
                    print e
            except Exception, e:
                print e
            transaction.commit_unless_managed(BILLING_DB)
            if   option == "localnumbers_contract_number":
                sd = get_signed(user, "localphone_services_contract")
                return sd.id
            elif option == "add_install":
                add_install = """<table border="1" cellpadding="0" cellspacing="0"><tbody>"""
                add_install += """
                        <tr>
                            <td style="width: 30px;">
                                <p align="center">
                                    <strong>%(number)s</strong></p>
                            </td>
                            <td colspan="2" style="width: 350px; ">
                                <p align="center">
                                    <strong>%(say_description)s</strong></p>
                            </td>
                            <td style="width: 70px; ">
                                <p align="center">
                                    <strong>%(say_count)s</strong></p>
                            </td>
                            <td style="width: 80px; ">
                                <p align="center">
                                    <strong>%(say_cost_one)s</strong></p>
                            </td>
                            <td style="width: 80px; ">
                                <p align="center">
                                    <strong>%(say_all)s</strong></p>
                            </td>
                        </tr>""" % {
                                    "number": u"№",
                                    "say_description": u"Описание",
                                    "say_count": u"Количество",
                                    "say_cost_one": u"Цена за ед.",
                                    "say_all": u"ВСЕГО",
                                    }
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                i = 0
                sum_all_with_nds = 0
                for number in param['numbers']:
                    i += 1
                    external_number_obj = ExternalNumber.objects.get(number=number)
                    connection_cost = ExternalNumberTarif.objects.get(id = external_number_obj.tarif_group).data_centr_price_connection



                    sum_all_with_nds += connection_cost.cost
                    add_install += """
                            <tr>
                                <td>
                                    <p align="center">
                                        %(number_install)s</p>
                                </td>
                                <td colspan="2">
                                    <p>
                                        %(service)s</p>
                                </td>
                                <td>
                                    <p align="center">
                                        1</p>
                                </td>
                                <td>
                                    <p align="center">
                                        %(cost_one)s</p>
                                </td>
                                <td>
                                    <p align="center">
                                        %(cost_one)s</p>
                                </td>
                            </tr>
                            """ % {
                                    "number_install": "1.%s" % i,
                                    "service": u"Инсталляция городского телефонного  номера %s" % number,
                                    "cost_one": connection_cost.cost / 1.18,
                                   }
                sum_all_without_nds = sum_all_with_nds / 1.18
                nds_all = sum_all_without_nds * 0.18
                add_install += """
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_cost_without_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(sum_all_without_nds)s</p></td>
                            </tr>
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(nds_all)s</p></td>
                            </tr>
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_cost_with_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(sum_all_with_nds)s</p></td>
                            </tr>""" % {
                                        "say_cost_without_nds": u"Всего без НДС",
                                        "say_nds": u"НДС 18%",
                                        "say_cost_with_nds": u"Итого с НДС",
                                        "sum_all_with_nds": sum_all_with_nds,
                                        "sum_all_without_nds": sum_all_without_nds,
                                        "nds_all": nds_all,
                                        }
                add_install += """</tbody></table>"""
                return add_install
            elif option == "add_abon":
                add_abon = """<table border="1" cellpadding="0" cellspacing="0"><tbody>"""
                add_abon += """
                    <tr>
                        <td style="width: 30px; ">
                            <p align="center">
                                <strong>%(number)s</strong></p>
                        </td>
                        <td style="width: 350px; ">
                            <p align="center">
                                <strong>%(say_description)s</strong></p>
                        </td>
                        <td style="width: 100px; text-align: center; vertical-align: middle; ">
                            <strong style="text-align: center; ">%(say_include_minutes)s</strong></td>
                        <td style="width: 70px; ">
                            <p align="center">
                                <strong>%(say_count)s</strong></p>
                        </td>
                        <td style="width: 80px; ">
                            <p align="center">
                                <strong>%(say_cost_one)s</strong></p>
                        </td>
                        <td style="width: 80px; ">
                            <p align="center">
                                <strong>%(say_all)s</strong></p>
                        </td>
                    </tr>""" % {
                                "number": u"№",
                                "say_description": u"Описание",
                                "say_include_minutes": u"Кол-во минут входящих в абон. плату",
                                "say_count": u"Количество",
                                "say_cost_one": u"Цена за ед.",
                                "say_all": u"ВСЕГО",
                                }
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                i = 0
                sum_all_with_nds = 0
                for number in param['numbers']:
                    i += 1
                    external_number_obj = ExternalNumber.objects.get(number=number)
                    tariff_obj = ExternalNumberTarif.objects.get(id = external_number_obj.tarif_group).data_centr_tariff
                    cost_one = tariff_obj.price_id.cost
                    count_min = tariff_obj.free_minutes
                    sum_all_with_nds += cost_one
                    add_abon += """
                            <tr>
                                <td>
                                    <p align="center">
                                        %(number_install)s</p>
                                </td>
                                <td>
                                    <p>
                                        %(service)s</p>
                                </td>
                                <td>
                                    <p align="center">
                                        %(count_min)s</p>
                                </td>
                                <td>
                                    <p align="center">
                                        1</p>
                                </td>
                                <td>
                                    <p align="center">
                                        %(cost_one)s</p>
                                </td>
                                <td>
                                    <p align="center">
                                        %(cost_one)s</p>
                                </td>
                            </tr>
                            """ % {
                                    "number_install": "2.%s" % i,
                                    "service": u"Абонентская плата за городской телефонный номер %s" % number,
                                    "count_min": count_min,
                                    "cost_one": round(cost_one / 1.18, 2),
                                   }
                sum_all_without_nds = round(sum_all_with_nds / 1.18, 2)
                nds_all = round(sum_all_without_nds * 0.18, 2)
                add_abon += """
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_cost_without_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(sum_all_without_nds)s</p></td>
                            </tr>
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(nds_all)s</p></td>
                            </tr>
                            <tr>
                                <td colspan="5" rowspan="1">
                                    <p align="right">
                                        <strong>%(say_cost_with_nds)s</strong></p>
                                </td>
                                <td>
                                    <p align="center">
                                    %(sum_all_with_nds)s</p></td>
                            </tr>
                            """ % {
                                   "say_cost_without_nds": u"Всего без НДС",
                                   "say_nds": u"НДС 18%",
                                   "say_cost_with_nds": u"Итого с НДС",
                                   "sum_all_with_nds": sum_all_with_nds,
                                   "sum_all_without_nds": sum_all_without_nds,
                                   "nds_all": nds_all,
                                   }
                add_abon += """</tbody></table>"""
                return add_abon
            elif option == "cost_over_free_minutes":
                cur = connections[BILLING_DB].cursor()
                try:
                    zone = []
                    zone_code = ['404', '408']
                    for code in zone_code:
                        cur.execute("SELECT price FROM tel_price WHERE tel_zone_id=%s and start_date<now() and end_date>now();", (code,))
                        zone.append(cur.fetchone()[0])
                except Exception, e:
                    print e
                transaction.commit_unless_managed(BILLING_DB)
                cost_over_free_minutes = """
                <p>%(z7495_7499)s</p>
                <p>%(z7812)s</p>
                """ % {
                       "z7495_7499": u"с номеров начинающихся с кода 7495 и 7499 - %s" % (float(zone[0]) / 1.18) + u" за минуту",
                       "z7812": u"с номеров начинающихся с кода 7812 - %s" % (float(zone[1]) / 1.18) + u" за минуту",
                       }
                return cost_over_free_minutes
            elif option == "localnumbers_region_index":
                return self.kwargs["region_index"]
            elif option == "localnumbers_region_name":
                rind = self.kwargs["region_index"]
                for reg in REGIONS:
                    if reg[0] == rind:
                        return reg[1]
                return ""
            elif option == "price_connect_sum":
                return "%.2f" % round(float(connect_price), 2)
            elif option == "price_connect_sum_with_nds":
                return "%.2f" % round(float(connect_price) * 1.18, 2)
            elif option == "price_connect_nds_of_sum":
                return "%.2f" % round(float(connect_price) * 1.18 - float(connect_price), 2)
            elif option == "price_abon_sum":
                return "%.2f" % round(float(abon_price), 2)
            elif option == "price_abon_sum_with_nds":
                return "%.2f" % round(float(abon_price) * 1.18, 2)
            elif option == "price_abon_nds_of_sum":
                return "%.2f" % round(float(abon_price) * 1.18 - float(abon_price), 2)
            elif option == "800_number_list":
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                action = param.get('number800', '-')
                table = u"""<table border="1" cellpadding="0" cellspacing="0" style="width: 790px;">
                               <tr>
                                   <th style="width: 30px;"><p align="center">№</p></th>
                                   <th><p align="center">Интеллектуальный номер</p></th>
                                   <th><p align="center">Категория номера</p></th>
                                   <th><p align="center">Наличие Web-smap</p></th>
                                   <th><p align="center">Логика услуги</p></th>
                                   <th><p align="center">Переадресация (номер с кодом страны/города или кодом DEF/поток Е1/IP-порт)</p></th>
                                   <th><p align="center">Населенный пункт, Административный центр региона закрепления физического номера</p></th>
                                   <th><p align="center">Оператор связи</p></th>
                               </tr>"""
                for counter, number in enumerate(param['numbers']):
                    ext_number = ExternalNumber.objects.get(number = number)
                    tariff = ext_number.tarif_group
                    table += '<tr><td>1.' + str(counter + 1) +'</td><td>' + number_format(number) + '</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
                table += u'</table>'
                return table
            elif option == "800_payments_list":
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                table = ''
                for counter, number in enumerate(param['numbers']):
                    ext_number = ExternalNumber.objects.get(number = number)
                    tariff = ext_number.tarif_group
                    tariff = ExternalNumberTarif.objects.get(pk = tariff)
                    payments = Number800Payments.objects.get(tariff = tariff)
                    category_cost = int(payments.category)
                    guaranteed_cost = int(payments.guaranteed)
                    connect_cost = int(payments.connect)
                    abon_cost = int(payments.abon)
                    reservation_cost = 2600
                    pause_cost = 2600
                    table += u'<p>2.' + str(counter + 1) + u' Тариф для Интеллектуального номера: ' + number_format(number) + u'</p>'
                    table += u"""<table border="1" cellpadding="0" cellspacing="0" style="width: 790px;">
                                   <tr>
                                       <th style="width: 30px;"><p align="center">№</p></th>
                                       <th style="width: 630px"><p align="center">Виды платежей</p></th>
                                       <th><p align="center">Размер оплаты руб. без НДС</p></th>
                                   </tr>"""
                    table += u'<tr><td colspan="3"><p align="center">Единовременные платежи</p></td></tr>'
                    table += u'<tr><td>1.</td><td>Единовременная плата за присвоение интеллектуального номера</td><td>' + str(connect_cost) + '</td></tr>'
                    table += u'<tr><td>2.</td><td>Плата за категорию номера</td><td>' + str(category_cost) + '</td></tr>'
                    table += u'<tr><td colspan="3"><p align="center">Ежемесячные платежи</p></td></tr>'
                    table += u'<tr><td>3.</td><td>Ежемесячный гарантированный платеж в счет оплаты трафика</td><td>' + str(guaranteed_cost) + '</td></tr>'
                    table += u'<tr><td>4.</td><td>Ежемесячная абонентская плата за один интеллектуальный номер</td><td>' + str(abon_cost) + '</td></tr>'
                    # table += u'<tr><td>5.</td><td>Ежемесячная абонентская плата за предоставление в пользование выделенного порта со скоростью до 2048 Кбит/с</td><td>x</td></tr>'
                    table += u'<tr><td colspan="3"><p align="center">Плата за дополнительные услуги</p></td></tr>'
                    table += u'<tr><td>5.</td><td>Бронирование интеллектуального номера</td><td>' + str(reservation_cost) + '</td></tr>'
                    table += u'<tr><td>6.</td><td>Приостановление обслуживания</td><td>' + str(pause_cost) + '</td></tr>'
                    table += u'<tr><td>7.</td><td>Смена тарифного плана в расчёте на один Интеллектуальный номер</td><td>1300</td></tr>'
                    table += u'<tr><td>9.</td><td>Корректировка «черного списка» номеров телефонов специалистами ОАО «Ростелеком» при подключенной у Заказчика услуге web-smap</td><td>130</td></tr>'
                    table += u'<tr><td>10.</td><td>Стандартная форма статистики. Предоставление статистики ежедневно (по рабочим дням).</td><td>780</td></tr>'
                    table += u'<tr><td>11.</td><td>Формирование и предоставление статистики по индивидуальному заказу Заказчика.</td><td>2600</td></tr>'
                    table += u'</table>'
                return table
            elif option == "800_stat":
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                stat = ''
                for counter, number in enumerate(param['numbers']):
                    stat += '<p>' + u'4.' + str(counter + 1) + u' Требования к индивидуальной форме статистики для номера ' + number_format(number) + u'</p><p align="center">[ОПИСАНИЕ ТРЕБОВАНИЙ]</p>'
                return stat
            elif option == "800_tariff_list":
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                limit = lambda x, y: u"от " + str(x) + u" до " + str(y) if x  and y and not y > 9000000 else u"свыше " + str(x - 1) if x else u"от " + str(y) if y and not y > 9000000 else u" "
                regions = dict([(str(r.id), r.name) for r in Number800Regiones.objects.all()])
                traffic_tariff = Number800TrafficTariff.objects.all()
                min_times = [t['min'] for t in traffic_tariff.values('min').distinct().order_by('min')]
                table = u"""<table border="1" cellpadding="0" cellspacing="0" style="width: 790px;">
                               <tr>
                                   <th rowspan="3"><p align="center">Ежемесячный объем трафика на один  номер ИСС, мин.</p></th>
                                   <th colspan="4"><p align="center">Размер оплаты, руб./мин. без НДС</p></th>
                               </tr>
                               <tr>
                                   <th colspan="4"><p align="center">Направление инициалиции вызова</p></th>
                               </tr>
                               <tr>
                                   <th><p align="center">от %(1)s</p></th>
                                   <th><p align="center">от %(2)s</p></th>
                                       <th><p align="center">от %(3)s</p></th>
                                   <th><p align="center">от %(4)s</p></th>
                               </tr>""" % regions
                for min_time in min_times:
                    tariffs = traffic_tariff.filter(min = min_time)
                    table += '<tr><td><p align="center">' + limit(tariffs[0].min, tariffs[0].max) + '</p></td>'
                    for t in tariffs:
                        table += '<td><p align="center">' + str(t.cost) + '</p></td>'
                    table += '</tr>'
                table += '</table>'
                text = ''
                for counter, number in enumerate(param['numbers']):
                    text += u'<p>2.' + str(counter + 1) + u' Тариф для Интеллектуального номера: ' + number_format(number) + u'</p>' + table
                return text
            elif option == "800_contract_number":
                try:
                    return FinDocSigned.objects.get(signed_by = user, findoc__slug = "800_contract").id
                except:
                    return ''
            elif option == "800_numbers":
                package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
                data = package_obj.data
                param = eval(data)
                numbers = [number_format(n) for n in param['numbers']]
                str_numbers = ', '.join(numbers)
                if len(numbers) > 1:
                    str_numbers = u"выделен Заказчику Интеллектуальный номер %s и закреплен " % str_numbers
                else:
                    str_numbers = u"выделены Заказчику Интеллектуальные номера %s и закреплены" % str_numbers
                return str_numbers
            return "(нету такого option)"

    result = [
        Variable(
            "localnumbers_contract_number",
            u"Номер договора на местную связь, к которому прикрепляется этот бланк заказа",
            ExternalNumberVarValue(
                "localnumbers_contract_number",
            )
        ),
    ]
    for reg in REGIONS:
        result.extend([
            Variable(
                "localnumbers_region_%s_index" % reg[0],
                u"Индекс региона %s" % reg[0],
                ExternalNumberVarValue(
                    "localnumbers_region_index",
                    region_index=reg[0],
                ),
            ),
            Variable(
                "localnumbers_region_%s_name" % reg[0],
                u"Имя региона %s" % reg[0],
                ExternalNumberVarValue(
                    "localnumbers_region_name",
                    region_index=reg[0],
                ),
            ),
        ])

    result.extend([
        Variable(
            "800_number_list",
            u"Список номеров 8-800",
            ExternalNumberVarValue(
                "800_number_list",
            ),
        ),
        Variable(
            "800_numbers",
            u"Строки вида: выделены Заказчику Интеллектуальные номера ... и закреплены",
            ExternalNumberVarValue(
                "800_numbers",
            ),
        ),
        Variable(
            "800_stat",
            u"Требования к статистике",
            ExternalNumberVarValue(
                "800_stat",
            ),
        ),
        Variable(
            "800_contract_number",
            u"Номер договора 800",
            ExternalNumberVarValue(
                "800_contract_number",
            ),
        ),
        Variable(
            "800_payments_list",
            u"Список платежей за номер 8-800",
            ExternalNumberVarValue(
                "800_payments_list",
            ),
        ),
        Variable(
            "800_tariff_list",
            u"Цены за входящую связь",
            ExternalNumberVarValue(
                "800_tariff_list",
            ),
        ),
        Variable(
             "add_install",
             u"Добавляет в таблицу строки с суммой по инсталяции номера",
             ExternalNumberVarValue(
                 "add_install",
             ),
        ),
        Variable(
              "add_abon",
              u"Добавляет в таблицу строки с суммой абонентской платы",
              ExternalNumberVarValue(
                  "add_abon",
              ),
         ),
        Variable(
               "cost_over_free_minutes",
               u"Возвращает список кодов и цену за минуту превышения лимита бесплатных минут",
               ExternalNumberVarValue(
                   "cost_over_free_minutes",
               ),
        ),
        Variable(
            "price_connect_sum",
            u"Цена полключения всех номеров",
            ExternalNumberVarValue(
                "price_connect_sum",
            ),
        ),
        Variable(
            "price_connect_sum_with_nds",
            u"Цена полключения всех номеров с НДС",
            ExternalNumberVarValue(
                "price_connect_sum_with_nds",
            ),
        ),
        Variable(
            "price_connect_nds_of_sum",
            u"Величина НДС от всей суммы подключения",
            ExternalNumberVarValue(
                "price_connect_nds_of_sum",
            ),
        ),
        Variable(
            "price_abon_sum",
            u"Суммарная абонентская плата",
            ExternalNumberVarValue(
                "price_abon_sum",
            ),
        ),
        Variable(
            "price_abon_sum_with_nds",
            u"Суммарная абонентская плата с НДС",
            ExternalNumberVarValue(
                "price_abon_sum_with_nds",
            ),
        ),
        Variable(
            "price_abon_nds_of_sum",
            u"Величина НДС от суммарной абонентской платы",
            ExternalNumberVarValue(
                "price_abon_nds_of_sum",
            ),
        ),
    ])

    return result

