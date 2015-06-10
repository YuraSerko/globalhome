# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from telnumbers.forms import SelectWithAddGroupForm
from django.core.exceptions import ValidationError

class AddExternalNumberForm(SelectWithAddGroupForm):
    
    numbers = forms.ChoiceField(
        label = _(u"Available local numbers"),
        choices = [],
        widget = forms.CheckboxSelectMultiple,
    )
    
    def __init__(self, *args, **kwargs):
        self.nbr = kwargs.pop("numbers_by_regions")
        
        super(AddExternalNumberForm, self).__init__(*args, **kwargs)

        ch = []
        for reg in self.nbr:
            nums = self.nbr[reg]
            for num in nums:
                name = "reg_%s_id_%s" % (reg, num.id)
                ch.append((name, num.number))
        self.fields["numbers"].choices = ch
        self.fields["numbers"].widget.form = self
        
        def num_clean(value):
            if not value:
                raise ValidationError(_(u"Please select at least one number!"))
            result = []
            import re
            rexp = r"reg_(\d+)_id_(\d+)"
            r = re.compile(rexp)
            for v in value:
                m = r.match(v)
                if m:
                    data = r.findall(v)[0]
                    if len(data) == 2:
                        id = int(data[1])
                        result.append(id)
            return result
        
        self.fields["numbers"].clean = num_clean
        

        
