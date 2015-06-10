# -*-coding=utf-8-*-

import re
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from django.db.models.fields import CharField
from django.core.validators import RegexValidator
from django.forms.fields import CharField as CharFormField
from south.modelsinspector import add_introspection_rules

MAC_RE = r'^([0-9a-fA-F]{2}([:-]?|$)){6}$'
mac_re = re.compile(MAC_RE)

MACS_RE = r'^([0-9a-fA-F]{2}([:]?)){6}([-])([0-9a-fA-F]{2}([:]?)){1,2}$'
macs_re = re.compile(MACS_RE)

validate_mac_addresses = RegexValidator(macs_re, _("Enter a valid range of MAC addresses."), 'invalid')
validate_mac_address = RegexValidator(mac_re, _("Enter a valid MAC address."), 'invalid')

class MACAddressFormField(CharFormField):
    default_error_messages = {
        'invalid': _(u'Enter a valid MAC address.'),
        }
    default_validators = [validate_mac_address]
    def clean(self, value):
        value = self.to_python(value).strip()
        return super(MACAddressFormField, self).clean(value)

    def get_internal_type(self):
        return "CharField"
class MACAddressField(CharField):
    empty_strings_allowed = False
    default_validators = [validate_mac_address]
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        CharField.__init__(self, *args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField,
                    'max_length': self.max_length}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

    def get_internal_type(self):
        return "CharField"
class MACAddressesFormField(CharFormField):
    default_error_messages = {
        'invalid': _(u'Enter a valid range of MAC addresses.'),
    }
    default_validators = [validate_mac_addresses]
    def clean(self, value):
        value = self.to_python(value).strip()
        return super(MACAddressesFormField, self).clean(value)

class MACAddressesField(CharField):
    default_validators = [validate_mac_addresses]
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 23
        CharField.__init__(self, *args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressesFormField,
                    'max_length': self.max_length}
        defaults.update(kwargs)
        return super(MACAddressesField, self).formfield(**defaults)

    def get_internal_type(self):
        return "CharField"

rules = [
    (
        (MACAddressField,), [],
        {
            "null": ["null", {"default": False}],
            "blank": ["blank", {"default": False}],
        }
    ),
         (
        (MACAddressesField,), [],
        {
            "null": ["null", {"default": False}],
            "blank": ["blank", {"default": False}],
        }
    ),
]

add_introspection_rules(rules, ["^installed_mikrotiks\.mac_address_field\.MACAddressField"])
add_introspection_rules(rules, ["^installed_mikrotiks\.mac_address_field\.MACAddressesField"])






