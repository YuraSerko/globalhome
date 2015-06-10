# coding: utf-8

MOSCOW = 1
STPETERSBURG = 2
NUMBER_800 = 3

REGIONS = (
    (MOSCOW, u"Москва"),
    (STPETERSBURG, u"Ст. Петербург"),
    (NUMBER_800, u"Федеральный номер 8-800"),
)
#### 8800 #####
ABON_SERVICE_TYPE = 14  # Абонентская плата за номер 8-800

NUMBER800_REGION = 3
NUMBER800_PRECODE = 4

RESERVATION_SERVICE_TYPE = 15
RESERVATION_TARIFF_ID = 123
RESERVATION_CONNECT_PRICE_ID = 1

PAUSE_SERVICE_TYPE = 16
PAUSE_TARIFF_ID = 124
PAUSE_CONNECT_PRICE_ID = 1

###############

def RegionTupleByRegion(region):
    "Возвращает tuple по указанному номеру региона"
    for t in REGIONS:
        if t[0] == region:
            return t

def RegionTupleByRegionName(region_name):
    "Возвращает tuple по указанному имени региона"
    for t in REGIONS:
        if t[1] == region_name:
            return t

_names_dict = {  # Тут хранятся соответствия регионов и названий телефонных зон
    RegionTupleByRegion(MOSCOW)[1]         : u"Moscow",
    RegionTupleByRegion(STPETERSBURG)[1]   : u"St. Petersburg",
    RegionTupleByRegion(NUMBER_800)[1]     : u"Federal number 8-800",
}

def get_region_zone(region):
    "Возвращает телефонную зону по указанному региону"
    from tariffs.models import TelZone
    rname = RegionTupleByRegion(region)[1]
    zone_name = _names_dict[rname]
    return TelZone.objects.get(name=zone_name)

def get_zone_region(zone):
    "Возвращает номер региона по указанной телефонной зоне"
    for key in _names_dict:
        if _names_dict[key] == zone.name:
            return RegionTupleByRegionName(key)[0]


from django.conf import settings
from django.db import connections, transaction
cur = connections[settings.BILLING_DB].cursor()
cur.execute("SELECT id,cost FROM billservice_addonservice")
tarif = cur.fetchall()
dc = dict(tarif)
cur.execute("SELECT id,about FROM external_numbers_tarif")
tarif_group = cur.fetchall()
dc_group = dict(tarif_group)
transaction.commit_unless_managed(using=settings.BILLING_DB)

def tarifTupleBytarif(region):
    "Возвращает tuple по указанному номеру региона"
    for t in tarif:
        if t[0] == region:
            return t

def tarifTupleBytarifName(region_name):
    "Возвращает tuple по указанному имени региона"
    for t in tarif:
        if t[1] == region_name:
            return t


def get_tarif_zone(region):
    "Возвращает телефонную зону по указанному региону"
    from externalnumbers.models import ExternalNumberTarif
    rname = tarifTupleBytarif(region)[1]
    zone_name = dc[rname]
    return ExternalNumberTarif.objects.get(name=zone_name)

def get_zone_tarif(zone):
    "Возвращает номер региона по указанной телефонной зоне"
    for key in dc:
        if dc[key] == zone.name:
            return tarifTupleBytarifName(key)[0]


def tarifTupleBytarif_group(region):
    "Возвращает tuple по указанному номеру региона"
    for t in tarif:
        if t[0] == region:
            return t

def tarifTupleBytarifName_group(region_name):
    "Возвращает tuple по указанному имени региона"
    for t in tarif:
        if t[1] == region_name:
            return t



def get_tarif_zone_group(region):
    "Возвращает телефонную зону по указанному региону"
    from externalnumbers.models import ExternalNumber
    rname = tarifTupleBytarif_group(region)[1]
    zone_name = dc_group[rname]
    return ExternalNumber.objects.get(tarif_group=zone_name)

def get_zone_tarif_group(zone):
    "Возвращает номер региона по указанной телефонной зоне"
    for key in dc_group:
        if dc_group[key] == zone.name:
            return tarifTupleBytarifName_group(key)[0]

