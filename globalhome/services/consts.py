# coding: utf-8
from django.utils.translation import ugettext_lazy as _

SERVICE_TELEMATIC = 1
SERVICE_LOCAL_TELEPHONE = 2
SERVICE_EQUIPMENT_RENTAL = 3

SERVICES_TYPES_CHOICES = (
    (SERVICE_TELEMATIC, _(u"Telematic services")),
    (SERVICE_LOCAL_TELEPHONE, _(u"Local phone number services")),
    (SERVICE_EQUIPMENT_RENTAL, _(u"Rental equipment service")),
)

PACKET_CONNECTING = 1
PACKET_DISCONNECTING = 2

PACKET_APPLICATION_CHOICES = (
    (PACKET_CONNECTING, _(u"Connecting")),
    (PACKET_DISCONNECTING, _(u"Detaching")),
)

