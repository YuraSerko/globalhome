# coding: utf-8

from django.db import models


class Category(models.Model):
    title = models.CharField(max_length = 400, null=True, blank=True)
    eng_title = models.CharField(max_length = 400, null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    avatars_amount = models.IntegerField(null=True, blank=True)
    main_description = models.CharField(max_length=1000, blank=True, verbose_name=u'Описание')
    category_description = models.CharField(max_length=1000, blank=True, verbose_name=u'Описание категории')
    html_title = models.CharField(max_length = 1000, null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    admin_weight = models.IntegerField(null=True, blank=True)
    show_venue_list = models.IntegerField(null=True, blank=True)
    title_genitive = models.CharField(max_length = 800, null=True, blank=True)
    title_title_dative = models.CharField(max_length = 800, null=True, blank=True)
    title_accusative = models.CharField(max_length = 800, null=True, blank=True)
    title_instrumental = models.CharField(max_length = 800, null=True, blank=True)
    title_prepositional = models.CharField(max_length = 800, null=True, blank=True)
    title_prefix = models.CharField(max_length = 600, null=True, blank=True)
    object_prefix = models.CharField(max_length = 600, null=True, blank=True)
    def __unicode__(self, *args):
        return self.title
    class Meta:
        db_table = 'tickets_category'
        verbose_name = u'Категория'
        verbose_name_plural = u'Категории'


class Tags(models.Model):
    title = models.CharField(max_length = 500, null=True, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, verbose_name=u'Категория')
    title_eng = models.CharField(max_length = 500, null=True, blank=True)
    alias = models.CharField(max_length = 500, null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    show = models.CharField(max_length = 500, null=True, blank=True)
    class Meta:
        db_table = 'tickets_tags'
        verbose_name = u'Теги'
        verbose_name_plural = u'Теги'
    def __unicode__(self):
        return self.alias


class Venue(models.Model):
    title = models.CharField(max_length = 400, null=True, blank=True)
    address = models.CharField(max_length = 800, null=True, blank=True)
    alias = models.CharField(max_length = 800, null=True, blank=True, unique = True) 
    region_id = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=9512, null=True, blank=True)
    image = models.CharField(max_length=400, null=True, blank=True)
    description_text = models.TextField(blank=True, null=True, verbose_name=u'Описание')
    def __unicode__(self):
        return self.title
    #===========================================================================
    # def save(self, first = False):
    #     print "It's save"
    #     if first:
    #         print "first"
    #         venue = Venue.objects.get(id = self.id)
    #         self.description_text = venue.description_text
    #         self.image = venue.image
    #     super(Venue, self).save()
    #===========================================================================
    class Meta:
        db_table = 'tickets_venue'
        verbose_name = u'Площадка'
        verbose_name_plural = u'Площадка'
 
 
class Event(models.Model):
    title = models.CharField(max_length = 400, null=True, blank=True)
    dates = models.CharField(max_length = 4400, null=True, blank=True) # List дат 
    alias = models.CharField(max_length = 400, null=True, blank=True, unique=True)
    link = models.CharField(max_length = 2900, null=True, blank=True)
    def __unicode__(self):
        return self.title
    class Meta:
        db_table = 'tickets_events'
        verbose_name = u'Событие'
        verbose_name_plural = u'События'


class BaseSubEvent(models.Model):
    str_date = models.CharField(max_length = 400, null=True, blank=True)
    str_time = models.CharField(max_length = 400, null=True, blank=True)
    event = models.ForeignKey(Event, blank=True, null=True, verbose_name=u'Событие')
    title = models.CharField(max_length = 400, null=True, blank=True, verbose_name = u'Название')
    #description = models.CharField(max_length=9512, null=True, blank=True)
    description_event = models.TextField(blank=True, null=True, verbose_name=u'Описание события')
    sub_event_id = models.CharField(max_length = 600, null=True, blank=True)
    category = models.ManyToManyField(Category, null=True, blank=True, verbose_name=u'Категория')
    date = models.CharField(max_length = 2400, null=True, blank=True)
    image = models.CharField(max_length = 800, null=True, blank=True)
    original_image = models.CharField(max_length = 800, null=True, blank=True)
    venue = models.ForeignKey(Venue, blank=True, null=True, verbose_name=u'Площадка')
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    ticket_count = models.IntegerField(null=True, blank=True)
    eticket_possible = models.CharField(max_length = 100, null=True, blank=True)
    tags = models.CharField(max_length = 1800, null=True, blank=True)
    tags_category = models.ManyToManyField(Tags, null=True, blank=True, verbose_name=u'Теги')
    type = models.CharField(max_length = 1800, null=True, blank=True)
    add_title = models.CharField(max_length = 4800, null=True, blank=True)
    end_date = models.CharField(max_length=4512, null=True, blank=True)
    categories_ids = models.CharField(max_length = 1800, null=True, blank=True)
    has_offer = models.CharField(max_length = 1800, null=True, blank=True)
    deleted = models.BooleanField( blank=True, verbose_name = u'Удалено')
    class Meta:
        managed = False
        abstract = True


class SubEvent(BaseSubEvent): 
    def __unicode__(self):
        return unicode(self.category) #or u''
    class Meta:
        db_table = 'tickets_subevents'
        verbose_name = u'Событие основное'
        verbose_name_plural = u'События основные'


#===============================================================================
# class Sectors(models.Model): #hotspot_sectors
#     title = models.CharField(max_length = 500, null=True, blank=True)
#     count = models.IntegerField(null=True, blank=True)
#     min_price = models.IntegerField(null=True, blank=True)
#     max_price = models.IntegerField(null=True, blank=True)
#     admission = models.CharField(max_length = 100, null=True, blank=True)
#     gateway_id = models.CharField(max_length = 1000, null=True, blank=True)
#     sectors_id_pomominalu = models.CharField(max_length = 3000, null=True, blank=True)
#     def __unicode__(self):
#         return self.id
#     class Meta:
#         db_table = 'tickets_sectors'
#         verbose_name = u'Сектора'
#         verbose_name_plural = u'Сектора'
#===============================================================================


#===============================================================================
# class Ticket(models.Model):
#     id_ticket_ponominalu = models.CharField(max_length = 500, null=True, blank=True)
#     raw = models.CharField(max_length = 500, null=True, blank=True)
#     seat = models.CharField(max_length = 500, null=True, blank=True)
#     price = models.CharField(max_length = 500, null=True, blank=True)
#     def __unicode__(self):
#         self.id_ticket_ponominalu
#     class Meta:
#         db_table = 'tickets_ticket'
#         #proxy = True
#         verbose_name = u'Билет'
#         verbose_name_plural = u'Билеты'
#===============================================================================

class Get_SubEvent(BaseSubEvent): #   SubEvent
    #id = models.AutoField(default = "", primary_key=True, blank=True)
    #subevent_ptr = models.ForeignKey(SubEvent, default = 1, blank=True, verbose_name=u'subevent_ptr')
    #subevent_ev = models.ForeignKey(SubEvent, null=True, blank=True, verbose_name=u'Событие')
    #sectors = models.ForeignKey(Sectors, null=True, blank=True, verbose_name=u'Сектора')
    #fk = models.ForeignKey(SubEvent, default = '', related_name = 'fk') #

    ##sectors_m2m = models.ManyToManyField(Sectors, null=True, blank=True, verbose_name=u'Сектора')
    commission = models.CharField(max_length = 500, null=True, blank=True)
    sectors_id_pomominalu = models.CharField(max_length = 9000, null=True, blank=True)
    #tickets = models.ManyToManyField(Ticket, null=True, blank=True, verbose_name=u'Билеты')
    def save(self):
        sub_ev = SubEvent.objects.get(id = self.id)
        self.sub_event_id = sub_ev.id
        self.str_date = sub_ev.str_date
        self.str_time = sub_ev.str_time
        self.event = sub_ev.event
        self.title = sub_ev.title
        #self.category = sub_ev.category
        self.date = sub_ev.date
        self.image = sub_ev.image
        self.original_image = sub_ev.original_image
        self.venue = sub_ev.venue
        self.min_price = sub_ev.min_price
        self.max_price = sub_ev.max_price
        self.ticket_count = sub_ev.ticket_count
        self.eticket_possible = sub_ev.eticket_possible
        #self.tags_category = sub_ev.tags_category
        self.type = sub_ev.type
        self.add_title = sub_ev.add_title
        self.end_date = sub_ev.end_date
        self.categories_ids = sub_ev.categories_ids
        self.has_offer = sub_ev.has_offer
        #self.description = sub_ev.description

        super(Get_SubEvent, self).save()
    class Meta:
        db_table = 'tickets_detail_description'
        #proxy = True
        verbose_name = u'Детальное описание события'
        verbose_name_plural = u'Детальное описание событий'
