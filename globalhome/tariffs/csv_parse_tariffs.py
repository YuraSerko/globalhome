# coding: utf-8
import csv
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from models import TariffGroup, TelZone, TelCode, Tariff
from django.db.utils import IntegrityError
import log

MOBILE_STR = u"Mobile"

def ddate(t):
    import datetime as rdt
    if type(t) is rdt.date:
        return t
    else:
        return t.date()

def tel_zone_is_mobile(tel_zone_name):
    """
        Возвращает True, если зона мобильная, если стационарная - False
    """
    return tel_zone_name.upper().find(MOBILE_STR.upper()) >= 0

def make_mobile_zone_name(tel_zone_name):
    """
        Возвращает имя мобильной зоны для указанной стационарной
    """
    return tel_zone_name + u" " + MOBILE_STR

def make_stat_zone_name(tel_zone_name):
    """
        Возвращает имя соответствующей стационарной зоны для переданной мобильной
    """
    return tel_zone_name[:len(tel_zone_name) - len(MOBILE_STR) - 1]


class CSVTariffParser():
    """
        Класс для парсинга тарифов из CSV файла и загоняния их в базу
    """

    def __init__(self, fname, billing_group_id, replace_names, replace_exists, autocreate_codes_and_zones, ignore_missing_zones, add_mobile_codes):
        self.debug = False
        
        self.messages = []
        self.warnings = []
        self.errors = []
        
        self.max_errors = 50
        self.max_warnings = 50
        self.max_messages = 50
        
        self.had_stop = False
        
        self.parsed_data = []
        self.parsed_tariffs = {}
        
        self.fname = fname
        self.replace_names = replace_names
        self.replace_exists = replace_exists
        self.autocreate = autocreate_codes_and_zones
        self.ignore_missing_zones = ignore_missing_zones
        self.add_mobile_codes = add_mobile_codes
        
        if self.debug: print datetime.now(), "parser.__init__()"; log.add("parser.__init__()")
        
        self.billing_group = TariffGroup.objects.get(id = billing_group_id)
        self.tel_zones = TelZone.objects.all()
        self.tel_codes = TelCode.objects.all()
        
        # подготовим dict с соответствием кода телефонной зоне
        self.tel_zone_by_code = {}
        for code in self.tel_codes:
            self.tel_zone_by_code[code.code] = code.tel_zone
        
        self.add_list = []
        self.err_count = 0
        self.warn_count = 0
        self.msg_count = 0

    def add_error(self, text):
        self.err_count += 1
        if len(self.errors) < self.max_errors:
            self.errors += [ text ]
        elif len(self.errors) == self.max_errors:
            self.errors += [_(u"Had more errors, but not displayed")]

    def add_warning(self, text):
        self.warn_count += 1
        if len(self.warnings) < self.max_warnings:
            self.warnings += [ text ]
        elif len(self.warnings) == self.max_warnings:
            self.warnings += [_(u"Had more warnings, but not displayed")]

    def add_message(self, text):
        self.msg_count += 1
        if len(self.messages) < self.max_messages:
            self.messages += [ text ]
        elif len(self.messages) == self.max_messages:
            self.messages += [_(u"Had more messages, but not displayed")]

    def ParseCSVFile(self):
        """
            Разбираю CSV файл и проверяю всякие ошибки только в файле
        """
        if self.debug: print datetime.now(), "parser.ParseCSVFile()"; log.add("parser.ParseCSVFile()")
        file = open(self.fname, "rb")
        reader = csv.reader(file, delimiter = ";")
        
        line_num = 0
        for values in reader:
            line_num += 1
            l = len(values)
            if l == 4 or l == 5:
                code = values[0]
                zone_name = values[1]
                price = float(values[2].replace(",", "."))
                try:
                    start_date = datetime.strptime(values[3], '%d.%m.%Y').date()
                except:
                    e_str = _(u"Parsing file: Cannot parse CSV file in line %(line)s! Wrong values number!").__unicode__()
                    self.add_error(e_str % { "line": line_num })
                    self.had_stop = True
                try:
                    end_date = datetime.strptime(values[4], '%d.%m.%Y').date()
                except Exception, e:
                    end_date = datetime.max.date()
                
                # вот тут запихиваем это дело куда надо
                self.parsed_data.append({
                    "tel_code.code" : code,
                    "tel_zone.name" : zone_name,
                    "price" : price,
                    "start_date" : start_date,
                    "end_date" : end_date,
                    "line_num" : line_num
                })
                
            else:
                e_str = _(u"Parsing file: Cannot parse CSV file in line %(line)s! Wrong values number!").__unicode__()
                seld.add_error( e_str % { "line": line_num } )
                self.had_stop = True
        
        file.close()

    def ParseData(self):
        """
            Разбираю ту инфу, которую удачно прочел из CSV файла. Проверяю на всякие ошибки/конфликты с базой
            формирую тут данные готовые для тарифов.
        """
        if self.debug: print datetime.now(), "parser.ParseData()"; log.add("parser.ParseData()")
        if not self.parsed_data:
            self.add_error(_(u"Parsing data: No parsed data from CSV file!!!"))
            self.had_stop = True
            return
        
        for item in self.parsed_data:
            # определяю телефонную зону по коду
            code = item["tel_code.code"]
            zone_name = item["tel_zone.name"]
            tel_zone = self.tel_zone_by_code.get(code)
            
            if not tel_zone:
                # укорачиваю
                ufounded = False
                
                for i in xrange(len(code)):
                    ucode = code[:-i]
                    
                    tz2 = self.tel_zone_by_code.get(ucode)
                    if tz2:
                        if tel_zone_is_mobile(tz2.name) == tel_zone_is_mobile(zone_name):
                            tel_zone = tz2
                            ufounded = True
                            break
                        else:
                            if not tel_zone_is_mobile(tz2.name):
                                if self.add_mobile_codes:
                                    # нашли стационарную зону по укороченному коду, а у нас - мобильная
                                    if self.debug: print "have stat but need mob!", ucode, tz2.name, "->", code, zone_name
                                    acode = code[:len(ucode)+2]
                                    if self.debug: print "adding code", acode
                                    c = TelCode()
                                    c.code = acode
                                    # найдем мобильную зону для этой стационарной
                                    tz3_name = make_mobile_zone_name(tz2.name)
                                    tz3 = self.tel_zones.get(name = tz3_name)
                                    c.tel_zone = tz3
                                    c.save()
                                    tel_zone = tz3
                                    self.tel_zone_by_code[acode] = tz3
                                    if self.debug: print "code", acode, "succesfully saved!\n"
                                    break
            
            if tel_zone:
                # вот тут формируем dict с изменениями тарифов
                p_tariff = self.parsed_tariffs.get(tel_zone)
                if p_tariff:
                    # сохраняю тариф с большей ценой
                    if item["price"] > p_tariff["price"]:
                        p_tariff["price"] = item["price"]
                        self.parsed_tariffs[tel_zone] = p_tariff
                    # тут проверяю на несоответствие дат
                    if p_tariff["start_date"] != item["start_date"] or p_tariff["end_date"] != item["end_date"]:
                        self.add_error(
                            (_(u"Parsing data: Mismatch of dates in lines %(line1)s and %(line2)s")) % 
                                { "line1": item["line_num"], "line2": p_tariff["line_num"] }
                        )
                        self.had_stop = True
                else:
                    p_tariff = {}
                    p_tariff["price"] = item["price"]
                    p_tariff["start_date"] = item["start_date"]
                    p_tariff["end_date"] = item["end_date"]
                    p_tariff["line_num"] = item["line_num"]
                    self.parsed_tariffs[tel_zone] = p_tariff
            else:
                if not self.ignore_missing_zones:
                    self.add_error(
                        (_(u"Parsing data: Code %(code)s with given name '%(zone_name)s' does not correspond to any telzone! See line %(line)s in your CSV file").__unicode__()) % 
                            { "code": item["tel_code.code"], "line": item["line_num"], "zone_name": item["tel_zone.name"] }
                    )
                    self.had_stop = True
                else:
                    self.add_warning(
                        (_(u"Parsing data: Code %(code)s with given name '%(zone_name)s' does not correspond to any telzone! See line %(line)s in your CSV file").__unicode__()) % 
                            { "code": item["tel_code.code"], "line": item["line_num"], "zone_name": item["tel_zone.name"] }
                    )
        
        if self.debug: print "errors count:", self.err_count

    def CalculateChanges(self):
        """
            Рассчитывает изменения в таблице тарифов и готовит списки с этими изменениями, чтобы потом разом всё применить
        """
        if self.debug: print datetime.now(), "parser.CalculateChanges()"; log.add("parser.CalculateChanges()")
        
        try:
            # переберем все распарсенные тарифы для импортирования
            for tel_zone in self.parsed_tariffs.keys():
                new_t = Tariff()
                new_t.tel_zone = tel_zone
                new_t.billing_group = self.billing_group
                new_t.start_date = self.parsed_tariffs[tel_zone]["start_date"]
                new_t.end_date = self.parsed_tariffs[tel_zone]["end_date"]
                new_t.price = self.parsed_tariffs[tel_zone]["price"]
                c_line = self.parsed_tariffs[tel_zone]["line_num"]
                
                self.add_list.append(new_t)
        except Exception, e:
            # непонятно, правда, откуда тут может быть эксцепшн, но все же...
            self.had_stop = True
            msg = "Exception in CalculateChanges!!! Message: " + str(e)
            self.add_error(
                msg
            )
            log.add(msg)

    def ApplyChanges(self):
        """
            Применяет рассчитанные изменения
        """
        if self.debug: print datetime.now(), "parser.ApplyChanges()"; log.add("parser.ApplyChanges()")
        try:
            for tariff in self.add_list:
                tariff.save()
            if self.debug: print datetime.now(), "parser.ApplyChanges() done"; log.add("parser.ApplyChanges() done")
        except Exception, e:
            self.had_stop = True
            msg = "Exception in ApplyChanges!!! Message: " + str(e)
            self.add_error(
                msg
            )
            log.add(msg)
