# coding: utf-8
from django.db import models
from django.conf import settings
from billing.managers import BillingManager
from billing.models import BillserviceAccount  # , BillservicePrepaidMinutes  # @UnresolvedImport
# from settings import BILLING_DB, GLOBALHOME_DB2  # @UnusedImport
from django.utils.translation import ugettext_lazy as _
from externalnumbers.models import ExternalNumber
# from django.template.defaultfilters import default  # @UnusedImport
# from dateutil.relativedelta import relativedelta  # @UnresolvedImport, @UnusedImport
from internet.models import Internet_persons_for_connection
# import datetime
from internet.billing_models import Tariff as BillingTariff
# import calendar

ACTIVE = 1
FREE = 2
NOT_AVAILABLE = 3
BLOCKED = 4
STATUSES = [
    (ACTIVE, u'Активен'),
    (FREE, u'Свободен'),
    (NOT_AVAILABLE, u'Не доступен'),
    (BLOCKED, u'Заблокирован'),
]

SELF_COST = 1
INCLUDE_IN_MAIN_COST = 2
FREE_COST = 3
STATUSES_COST = [
                 (SELF_COST, u'Обычная оплата (1 заказ = 1 платежная запись)'),
                 (INCLUDE_IN_MAIN_COST, u'Объединять стоимость с главным заказом (2 заказа = 1 платежная запись)'),
                 (FREE_COST, u'Не учитывать стоимость данного заказа (1 заказ = 0 платежных записей)'),
]

TELEPHONY = 1
DATA_CENTR = 2
INTERNET = 3
SECTIONS_TYPE = [
                 (TELEPHONY, u'Телефония'),
                 (DATA_CENTR, u'Дата-центр'),
                 (INTERNET, u'Интернет'),
]


class Status_zakaza(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    status = models.CharField(max_length=75)
    about = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return self.status

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Status_zakaza, self).save(*args, **kwargs)

    class Meta:
        db_table = "data_centr_status_zakaza"
        verbose_name = _(u"Status zakaza")
        verbose_name_plural = _(u"Status zakaza")


class Status_ip(models.Model):
    id = models.AutoField(primary_key=True , blank=True)
    status = models.CharField(max_length=75)
    about = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return self.status

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Status_ip, self).save(*args, **kwargs)

    class Meta:
        db_table = "data_centr_status_ip"
        verbose_name = _(u"Status IP")
        verbose_name_plural = _(u"Status IP")


class Service_type(models.Model):
    id = models.AutoField(primary_key=True , blank=True)
    service = models.CharField(max_length=75)
    about = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return self.service

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        super(Service_type, self).save(*args, **kwargs)
#        bill_acc_all = BillserviceAccount.objects.all()
#        for bill_acc in bill_acc_all:
#            Limit_connection_service.create_limit_for_new_user(bill_acc=bill_acc, service_type_obj=self)
        return self

#    def delete(self, *args, **kwargs):
#        kwargs['using'] = settings.BILLING_DB
#        print 'delete'
#        print 'self = %s' % self.id
#        super(Service_type, self).delete(*args, **kwargs)


    class Meta:
        db_table = "data_centr_service_type"
        verbose_name = _(u"Service type")
        verbose_name_plural = _(u"Service type")


class Price(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=100)
    cost = models.FloatField()
    def __unicode__(self):
        return self.name + '(' + str(self.cost) + ')'

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Price, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_price"
        verbose_name = _(u"Price data centr")
        verbose_name_plural = _(u"Price data centr")


# class Port(models.Model):
#    id = models.AutoField(primary_key=True, blank=True)
#    name = models.CharField(max_length=50)
#    about = models.CharField(max_length=255, blank=True)
#    def __unicode__(self):
#        return self.name
#
#    objects = BillingManager()
#
#    def save(self, *args, **kwargs):
#        kwargs['using'] = settings.BILLING_DB
#        return super(Port, self).save(*args, **kwargs)
#
#    class Meta:
#        managed = True
#        db_table = "data_centr_port"
#        verbose_name = _(u"Port")
#        verbose_name_plural = _(u"Ports")


class IP(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=50)
    section_type = models.IntegerField(default=2, verbose_name=_(u"Section type"))
    status_ip = models.ForeignKey(Status_ip)
    price_id = models.ForeignKey(Price)
    about = models.CharField(max_length=255, blank=True)
    def __unicode__(self):
        return self.name

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(IP, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_ip"
        verbose_name = _(u"IP")
        verbose_name_plural = _(u"IPs")


class OS(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=50)
    about = models.CharField(max_length=255, blank=True)
    price_id = models.ForeignKey(Price)
    def __unicode__(self):
        return self.name

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(OS, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_os"
        verbose_name = _(u"OS")
        verbose_name_plural = _(u"OSs")


class Tariff(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    section_type = models.IntegerField(default=TELEPHONY, choices=SECTIONS_TYPE, verbose_name=_(u"Section type"))
    service_type = models.ForeignKey(Service_type)
    for_person = models.ManyToManyField(Internet_persons_for_connection, blank=True, null=True)
    name = models.CharField(max_length=50)
    equipment = models.CharField(max_length=255, null=True, blank=True)
    tower_casing = models.BooleanField(default=False)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    depth = models.IntegerField(null=True, blank=True)
    cpu = models.CharField(max_length=50, null=True, blank=True)
    ram = models.CharField(max_length=50, null=True, blank=True)
    hdd = models.CharField(max_length=50, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    port = models.CharField(max_length=50, null=True, blank=True)
    ip = models.IntegerField(null=True, blank=True)
    socket = models.CharField(max_length=50, blank=True)
    electricity = models.CharField(max_length=50, blank=True)
    free_minutes = models.IntegerField(null=True, blank=True)
    tel_zone = models.IntegerField(null=True, blank=True)
    speed_inet = models.FloatField(null=True, blank=True)
    garant = models.BooleanField(default=False)
    about = models.CharField(max_length=255, blank=True)
    price_id = models.ForeignKey(Price)
    billing_tariff = models.ForeignKey(BillingTariff, null=True, blank=True)
    individual = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Tariff, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_tariff"
        verbose_name = _(u"Tariff")
        verbose_name_plural = _(u"Tariffs")


class Price_connection(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=100)
    cost = models.FloatField()
    def __unicode__(self):
        return self.name + '(' + str(self.cost) + ')'

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Price_connection, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_price_connection"
        verbose_name = _(u"Price connection")
        verbose_name_plural = _(u"Price connection")


class Type_ram(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    type = models.CharField(max_length=255)
    def __unicode__(self):
        return '%s' % self.type

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Type_ram, self).save(*args, **kwargs)


class Slots_ram(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    type_ram = models.ForeignKey(Type_ram, null=True)
    count_slots = models.IntegerField(null=True)
    def __unicode__(self):
        return u'%s (%s слот(а/ов))' % (self.type_ram, self.count_slots)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Slots_ram, self).save(*args, **kwargs)


class Type_hdd(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    type = models.CharField(max_length=255)
    def __unicode__(self):
        return '%s' % self.type

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Type_hdd, self).save(*args, **kwargs)


class Slots_hdd(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    type_hdd = models.ForeignKey(Type_hdd, null=True)
    count_slots = models.IntegerField(null=True)
    def __unicode__(self):
        return u'%s (%s слот(а/ов))' % (self.type_hdd, self.count_slots)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Slots_hdd, self).save(*args, **kwargs)


class Motherboards(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    form_factor = models.CharField(max_length=255, verbose_name=u"Формфактор")
    connector_type = models.CharField(max_length=255, verbose_name=u"Тип разъема")
    chipset = models.CharField(max_length=255, verbose_name=u"Чипсет")
    slots_ram = models.ManyToManyField(Slots_ram, verbose_name=u"Слоты оперативной памяти")
    max_ram = models.IntegerField(null=True, verbose_name=u'Максимальный объем оперативной памяти, (Гб)')
    supply_connector = models.CharField(max_length=255, verbose_name=u'Коннектор питания')
    built_in_video = models.CharField(max_length=255, verbose_name=u'Встроенное видео')
    built_in_audio = models.CharField(max_length=255, verbose_name=u'Встроенное аудио')
    slots_hdd = models.ManyToManyField(Slots_hdd, verbose_name=u'Слоты для винчестера')
    external_connectors = models.TextField(null=True, verbose_name=u'Внешние разъемы')
    slots = models.CharField(max_length=255, verbose_name=u'Слоты')
    physical_sizes = models.CharField(max_length=255, verbose_name=u'Физические размеры')
    def __unicode__(self):
        return '%s (%s, %s)' % (self.form_factor, self.connector_type, self.chipset)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Motherboards, self).save(*args, **kwargs)


class CPU(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    processor_family = models.CharField(max_length=255, null=True, verbose_name=u"Семейство процессора")
    quantity_of_kernels = models.IntegerField(null=True, verbose_name=u"Количество ядер")
    internal_clock_rate = models.IntegerField(null=True, verbose_name=u"Внутренния тактовая частота, МГц")
    data_bus_frequency = models.IntegerField(null=True, verbose_name=u"Частота шины данных, МГц")
    volume_cache_of_memory_1 = models.IntegerField(null=True, verbose_name=u"Кэш 1-ого уровня, Кб")
    volume_cache_of_memory_2 = models.IntegerField(null=True, verbose_name=u"Кэш 2-ого уровня, Кб")
    volume_cache_of_memory_3 = models.IntegerField(null=True, verbose_name=u"Кэш 3-ого уровня, Кб")
    def __unicode__(self):
        return u'%s %s МГц' % (self.processor_family, self.internal_clock_rate)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(CPU, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_cpu"
        verbose_name = _(u"CPU")
        verbose_name_plural = _(u"CPUs")


class HDD(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=u"Фирма производитель")
    interface = models.ForeignKey(Type_hdd, null=True, verbose_name=u"Интерфейс")
    hdd_capacity = models.FloatField(null=True, verbose_name=u"Емкость накопителя, Гб")
    type_hdd = models.CharField(max_length=255, null=True, verbose_name=u"Тип жесткого диска")
    form_factor = models.CharField(max_length=255, null=True, verbose_name=u"Форм-фактор")
    buffer_volume = models.IntegerField(null=True, verbose_name=u"Объем буфера, Мб")
    rotational_speed_of_a_spindle = models.IntegerField(null=True, verbose_name=u"Скорость вращения шпинделя, об/мин")
    data_transmission_rate = models.FloatField(null=True, verbose_name=u"Скорость передачи данных, Мб/сек")
    max_level_of_noise = models.IntegerField(null=True, verbose_name=u"Максимальный уровень шума, дБ")
    max_power_consumption = models.FloatField(null=True, verbose_name=u"Максимальная потребляемая мощность, Вт")
    physical_sizes = models.CharField(max_length=255, null=True, verbose_name=u"Физические размеры")
    def __unicode__(self):
        return u'%s Гб, %s' % (self.hdd_capacity, self.interface)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(HDD, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_hdd"
        verbose_name = _(u"HDD")
        verbose_name_plural = _(u"HDDs")


class RAM(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, null=True, verbose_name=u"Фирма производитель")
    assignment = models.CharField(max_length=255, null=True, verbose_name=u"Назначение")
    type_ram = models.ForeignKey(Type_ram, null=True, blank=True, verbose_name=u"Тип памяти")
    memory_size = models.IntegerField(null=True, verbose_name=u"Объем памяти, Мб")
    memory_frequency = models.IntegerField(null=True, verbose_name=u"Частота памяти, МГц")
    cooling = models.CharField(max_length=255, null=True, verbose_name=u"Охлаждение")
    effective_throughput = models.IntegerField(null=True, verbose_name=u"Эффективная пропускная способность, Мб/сек")
    def __unicode__(self):
        return u'%s Мб, %s МГц' % (self.memory_size, self.memory_frequency)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(RAM, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_ram"
        verbose_name = _(u"RAM")
        verbose_name_plural = _(u"RAM")


class Servers(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=u'Название сервера')
    motherboard = models.ForeignKey(Motherboards, verbose_name=u'Материнская плата')
    cpu = models.ForeignKey(CPU, verbose_name=u'Процессор')
    hdd = models.ManyToManyField(HDD, verbose_name=u'Жесткий диск')
    ram = models.ManyToManyField(RAM, verbose_name=u'Оперативная память')
    count_unit = models.IntegerField(verbose_name=u'Количество юнитов')
    count_port = models.IntegerField(verbose_name=u'Количество портов')
    count_sockets = models.IntegerField(verbose_name=u'Количество розеток')
    electricity = models.IntegerField(verbose_name=u'Потребляемое электричество, Вт')
    depth = models.FloatField(verbose_name=u'Глубина сервера, мм')
    count_servers = models.IntegerField(verbose_name=u'Количество серверов, шт')
    tariff = models.ForeignKey(Tariff, null=True, blank=True, verbose_name=_(u"Tariff"))
    def __unicode__(self):
        return '%s' % self.name

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Servers, self).save(*args, **kwargs)


class Sockets(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=u'Название')
    number_socket = models.IntegerField(verbose_name=u'Номер розетки')
    adrress = models.ManyToManyField('Address_dc', null=True, blank=True, verbose_name=u'Адрес в ДЦ')
    block_of_socket = models.ForeignKey('Blocks_of_socket', verbose_name=u'Блок розеток')
    status_socket = models.IntegerField(default=FREE, choices=STATUSES, verbose_name=u'Статус розетки')
    def __unicode__(self):
        return self.name


    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Sockets, self).save(*args, **kwargs)

    @classmethod
    def create(Sockets, name, number_socket, block_of_socket):
        socket = Sockets(name=name, number_socket=number_socket, block_of_socket=block_of_socket)
        socket.save()
        return socket


class Blocks_of_socket(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=u'Название')
    count_sockets = models.IntegerField(verbose_name=u'Количество розеток')
    rack = models.ForeignKey('Rack', verbose_name=u'Серверная стойка')
    def __unicode__(self):
        return self.name

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        if self.pk is None:
            self.name = 'Electro-%s-%s' % (self.rack.name, len(Blocks_of_socket.objects.filter(rack=self.rack)) + 1)
            super(Blocks_of_socket, self).save()
            count_sockets = self.count_sockets
            for i in range(count_sockets):
                Sockets.create(name='%s-r%s' % (self.name, i + 1), number_socket=i + 1, block_of_socket=self)
        else:
            super(Blocks_of_socket, self).save(*args, **kwargs)
        return self


class Ports(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    number_port = models.IntegerField(verbose_name='Номер порта')
    adrress = models.ManyToManyField('Address_dc', null=True, blank=True, verbose_name='Адрес в ДЦ')
    speed = models.FloatField(default=100, verbose_name='Скорость порта')
    vlan = models.IntegerField(null=True, blank=True)
    status_port = models.IntegerField(default=FREE, choices=STATUSES, verbose_name='Статус порта')
    switch = models.ForeignKey('Switchs', verbose_name='Коммутатор')
    prefix_interface = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

    @classmethod
    def create(Ports, name, number_port, speed, switch, prefix_interface):
        port = Ports(name=name, number_port=number_port, speed=speed, switch=switch, prefix_interface=prefix_interface)
        port.save()
        return port


class Switchs(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    ip = models.IPAddressField(verbose_name='IP-адрес коммутатора')
    count_port = models.IntegerField(verbose_name='Количество портов')
    speed = models.FloatField(default=100, verbose_name='Скорость портов в свитче')
    rack = models.ForeignKey('Rack', verbose_name='Серверная стойка')
    prefix_interface = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

    def save(self):
        if self.pk is None:
            self.name += '-%s' % (len(Switchs.objects.filter(rack=self.rack)) + 1)
            super(Switchs, self).save()
            print 'name = %s' % self.name
            count_port = self.count_port
            for i in range(count_port):
                Ports.create(name='%s-p%s' % (self.name, i + 1), number_port=i + 1, speed=self.speed, switch=self, prefix_interface='%s/%s' % (self.prefix_interface, i + 1))
        else:
            super(Switchs, self).save()
        return self


class Units(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    number_unit = models.IntegerField(verbose_name='Номер юнита')
    address = models.ManyToManyField('Address_dc', null=True, blank=True, verbose_name='Адрес в ДЦ')
    rack = models.ForeignKey('Rack', verbose_name='Серверная стойка')
    status_unit = models.IntegerField(default=FREE, choices=STATUSES, verbose_name='Статус юнита')
    def __unicode__(self):
        return self.name

    @classmethod
    def create(Unit, name, number_unit, rack):
        unit = Unit(name=name, number_unit=number_unit, rack=rack)
        unit.save()
        return unit


class Rack(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, verbose_name=u'Название')
    depth = models.FloatField(verbose_name=u'Глубина стойки, мм')
    count_unit = models.IntegerField(verbose_name=u'Количество юнитов')
    max_unit_for_server = models.FloatField(verbose_name=u'Максимальная высота сервера в юнитах')
    ups = models.CharField(max_length=255, verbose_name=u'Бесперебойное питание')
    is_active = models.BooleanField(default=True, verbose_name=u'Активность')
    def __unicode__(self):
        return self.name

    def save(self):
        if self.pk is None:
            super(Rack, self).save()
            count_units = self.count_unit
            for i in range(count_units):
                Units.create(name='%s-u%s' % (self.name, i + 1), number_unit=i + 1, rack=self)
        else:
            super(Rack, self).save()
        return self


class Address_dc(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255)
    rack = models.ForeignKey(Rack, verbose_name=u'Серверная стойка')
    date_create = models.DateTimeField()
    date_close = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        units_qs = Units.objects.filter(rack=self.rack, address=self)
        number_unit = ', '.join(str(i.number_unit) for i in units_qs) or u'нет'
        ports_qs = Ports.objects.filter(adrress=self)
        number_port = ', '.join(str(i.number_port) for i in ports_qs) or u'нет'
        socket_qs = Sockets.objects.filter(adrress=self)
        number_socket = ', '.join(str(i.number_socket) for i in socket_qs) or u'нет'
        description = u'%s (стойка: %s, юниты: № = %s, порты: № = %s, розетки: № = %s)' % (self.name, self.rack, \
                                                                                           number_unit, number_port, number_socket)
        return description


class Address_dc_full(Address_dc):
    class Meta:
        proxy = True


class Server_assembly(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    cpu = models.ForeignKey(CPU)
    ram = models.IntegerField()
    hdd = models.IntegerField()
    ssd = models.IntegerField()
    def __unicode__(self):
        return u'id: %s, cpu: %s, ram: %s, hdd: %s, ssd: %s' % (self.id, self.cpu, self.ram, self.hdd, self.ssd)

# from django.utils.html import format_html
# from django.template.defaultfilters import escape
# from django.core.urlresolvers import reverse
# from externalnumbers.models import ExternalNumber
class Zakazy(models.Model):
    id = models.AutoField(primary_key=True, blank=True, verbose_name=u'Номер заказа')
    section_type = models.IntegerField(default=TELEPHONY, choices=SECTIONS_TYPE, verbose_name=_(u"Section type"))
    service_type = models.ForeignKey(Service_type, verbose_name=_(u"Service type"))
    main_zakaz = models.IntegerField(null=True, blank=True)
    tariff = models.ForeignKey(Tariff, verbose_name=_(u"Tariff"), null=True, blank=True)
    ext_numbers = models.ManyToManyField(ExternalNumber, blank=True, null=True, verbose_name=_(u"City numbers"))
    equipment = models.CharField(max_length=100, null=True, blank=True, verbose_name=_(u"Equipment"))
    count_of_units = models.IntegerField(null=True, blank=True, verbose_name=_(u"Count of units"))
    count_of_port = models.IntegerField(null=True, blank=True, verbose_name=_(u"Count of port"))
    socket = models.IntegerField(null=True, blank=True, verbose_name=_(u"Socket"))
#    port = models.ManyToManyField(Port, blank=True, verbose_name=_(u"Port"))
    count_ip = models.IntegerField(default=0, verbose_name=u'Количество ip')
    ip = models.ManyToManyField(IP, blank=True, verbose_name=_(u"IP"))
    electricity = models.IntegerField(null=True, blank=True, verbose_name=_(u"Electricity"))
    bill_account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"))
    status_zakaza = models.ForeignKey(Status_zakaza, verbose_name=_(u"Status zakaza"))
    date_create = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date create"))
    date_activation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date activation"))
    date_end_test_period = models.DateTimeField(null=True, blank=True, verbose_name=u'Дата окончания тестового периода')
    date_deactivation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date deactivation"))
    cost = models.FloatField(null=True, blank=True, verbose_name=_(u"Cost"))
    status_cost = models.IntegerField(default=SELF_COST, choices=STATUSES_COST, verbose_name=u'Вид оплаты')
    connection_cost = models.ForeignKey(Price_connection, default=1, verbose_name=_(u"Price connection"))
    about = models.CharField(max_length=255, null=True, blank=True, verbose_name=_(u"Дополнительные сведения"))  # Заменил verbose_name=_(u"About")
    city = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=150, null=True, blank=True)
    house = models.CharField(max_length=50, null=True, blank=True)
    server = models.ForeignKey(Servers, null=True, blank=True, verbose_name=u'Сервер')
    server_assembly = models.ForeignKey(Server_assembly, null=True, blank=True, verbose_name=u'Конфигурация сервера')
    address_dc = models.ForeignKey(Address_dc, null=True, blank=True, verbose_name=u'Адрес в дата-центре')
    delivery_address = models.CharField(max_length=255, null=True, blank=True)
    delivery_telephone = models.CharField(max_length=127, null=True, blank=True)
    delivery = models.ForeignKey(Tariff, related_name='delivery_tariff', null=True, blank=True, db_column='delivery')

    def __unicode__(self):
        return str(self.id)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Zakazy, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "data_centr_zakazy"
        verbose_name = _(u"Zakazy")
        verbose_name_plural = _(u"Zakazy")


class Priority_of_services(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    bill_account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"))
    zakaz_id = models.IntegerField()
    priority = models.IntegerField()
    def __unicode__(self):
        return str(self.id)

    objects = BillingManager()

    '''
    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Priority_of_services, self).save(*args, **kwargs)
    '''

    class Meta:
        db_table = "priority_of_services"
        verbose_name = _(u"Priority of service")
        verbose_name_plural = _(u"Priority of services")


class Data_centr_payment(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    year = models.IntegerField(verbose_name=_(u"Year"))
    month = models.IntegerField(verbose_name=_(u"Month"))
    bill_account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"))
    zakaz = models.ForeignKey(Zakazy, verbose_name=_(u"Zakazy"))
    cost = models.FloatField(default=0, verbose_name=_(u"Cost"))
    payment_date = models.DateField(null=True, blank=True, verbose_name=_(u"Payment date"))
    every_month = models.BooleanField(default=True, verbose_name=_(u"Every month"))
    postdate = models.BooleanField(default=False, verbose_name=_(u"Postdate"))
    message_on_warning = models.IntegerField(default=0, verbose_name=_(u"Message on warning"))
    def __unicode__(self):
        return str(self.id)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Data_centr_payment, self).save(*args, **kwargs)

    class Meta:
        db_table = "data_centr_payment_for_service"
        verbose_name = _(u"Payment services")
        verbose_name_plural = _(u"Payment services")


class Limit_connection_service(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    bill_acc = models.ForeignKey(BillserviceAccount)
    service_type = models.ForeignKey(Service_type, verbose_name=_(u"Service type"))
    count_limit = models.IntegerField(default=3)
    def __unicode__(self):
        return str(self.id)

    @staticmethod
    def create_limit_for_new_user(bill_acc, service_type_obj=None):
        if not service_type_obj:
            service_type_all = Service_type.objects.all()
        else:
            service_type_all = [service_type_obj]
        for service_type_obj in service_type_all:
            limit_qs = Limit_connection_service.objects.filter(
                                                 bill_acc=bill_acc,
                                                 service_type=service_type_obj,
                                                 )
            if not limit_qs:
                limit_obj = Limit_connection_service(
                                                     bill_acc=bill_acc,
                                                     service_type=service_type_obj,
                                                     )
                limit_obj.save()

    class Meta:
        unique_together = ('bill_acc', 'service_type',)
        db_table = 'data_centr_limit_connection_service'



class Add_free_internet_zakaz(models.Model):
    class Meta:
        verbose_name_plural = u"Создать заказ на бесплатный интернет"
        managed = False


class Restore_zakaz(models.Model):
    class Meta:
        verbose_name_plural = u"Восстановить заказ"
        managed = False


# class Return_payment(models.Model):
#    id = models.AutoField(primary_key=True, blank=True)
#    payment = models.ForeignKey(Data_centr_payment)
#    return_payment = models.BooleanField(default=False)
#    send_mail = models.BooleanField(default=False)
#
#    objects = BillingManager()
#
#    class Meta:
#        verbose_name_plural = u"Возврат денежных средств"
#
#    def __unicode__(self):
#        return u'%s' % self.id
#
#    def save(self, *args, **kwargs):
#        kwargs['using'] = settings.BILLING_DB
#        return super(Zakazy, self).save(*args, **kwargs)

DELIVERY_STATUS_CHOICES = (
        (u'В обработке', u'В обработке'),
        (u'Доставлено', u'Доставлено'),
    )

class ZakazyDelivery(models.Model):
    id = models.AutoField(primary_key=True, blank=True, verbose_name=u'Номер доставки')
    zakazy_list = models.ManyToManyField(Zakazy, related_name='delivery_zakazy_list', blank=True, null=True, verbose_name=u'Номера заказов')  # название промежуточной таблицы
    zakazy_write_off = models.ForeignKey(Zakazy, related_name='delivery_zakazy_write_off', blank=True, null=True, verbose_name=u'Номер заказа с оплатой доставки')
    paid = models.BooleanField(default=False, verbose_name=u'Оплачено')
    delivery_status = models.CharField(max_length=100, default='В обработке', choices=DELIVERY_STATUS_CHOICES, blank=True, null=True, verbose_name=u'Статус доставки')
    class Meta:
        db_table = 'data_centr_zakazy_delivery'
        verbose_name = _(u"Доставка заказа")
        verbose_name_plural = _(u"Доставка заказов")
    def zakazy_list_view(self):
        return u" %s" % (u", ".join([str(Zakazy.id) for Zakazy in self.zakazy_list.all()]))
    zakazy_list_view.short_description = u'Номера заказов для доставки'
