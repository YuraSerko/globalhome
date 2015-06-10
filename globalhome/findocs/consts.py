# coding: utf-8
from django.utils.translation import ugettext_lazy as _

FIN_DOC_CONTRACT = 1
FIN_DOC_ORDERFORM = 2
FIN_DOC_ACT_OF_HANDOVER = 3
FIN_DOP_DOC_CLOSE_ACCOUNT = 4

FIN_DOCS_TYPES_CHOICES = (
    (FIN_DOC_CONTRACT, _(u"Contract")),
    (FIN_DOC_ORDERFORM, _(u"Order form")),
    (FIN_DOC_ACT_OF_HANDOVER, _(u"Act of handover")),
    (FIN_DOP_DOC_CLOSE_ACCOUNT, _(u"Dop doc close account")),
)
