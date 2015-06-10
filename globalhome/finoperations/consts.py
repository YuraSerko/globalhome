# coding: utf-8
from django.utils.translation import ugettext as _

OP_TYPE_WITHDRAW = 1
OP_TYPE_DEPOSIT = 2

OPERATION_TYPES = (
    (OP_TYPE_WITHDRAW, _(u"Withdraw funds")),
    (OP_TYPE_DEPOSIT, _(u"Depositing funds")),
)

def operation_str_by_int(iop):
    for op in OPERATION_TYPES:
        if op[0] == iop:
            return op[1]


