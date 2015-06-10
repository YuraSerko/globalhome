# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
import re
from telnumbers.models import TelNumber
from django.utils.safestring import mark_safe


#from models import

class EditTelNumbersGroupForm(forms.Form):
    name = forms.CharField(
        label = mark_safe(_(u"Group name").__unicode__()),
        widget = forms.TextInput(
            attrs = { "size": "50" },
        ),
    )
    numbers = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple,
        choices = [],
        label = mark_safe(_(u"Internal numbers").__unicode__()),
        help_text = _(u"Please select phones in this group:"),
    )

    def __init__(self, data = None, numbers = None, existing_groups = None,  group = None):
        #print group.numbers.all()


        numchoices = []
        self.existing_groups = existing_groups
        for num in numbers:
            numchoices.append((num.id, num.get_view_name()))
        self.base_fields["numbers"].choices = numchoices
        self.base_fields["numbers"].required = False

        self.group = group

        if group:
            self.base_fields["name"].initial = group.name
            self.base_fields["numbers"].initial = [num.id for num in group.numbers.all()]
        else:
            self.base_fields["name"].initial = ""
            self.base_fields["numbers"].initial = []

        self.base_fields['numbers'].required = True

        super(EditTelNumbersGroupForm, self).__init__(data)

    def clean_name(self):
        name = self.cleaned_data["name"]
        exc = forms.ValidationError(_(u"Group with this name already exists!"))
        if name:
            for g in self.existing_groups:
                if g.name == name:
                    if not self.group:
                        raise exc
                    else:
                        if g != self.group:
                            raise exc
        return name

    def clean_numbers(self):
        numbers = self.cleaned_data["numbers"]
        if not numbers:
            raise forms.ValidationError(_(u"Please select at least one number!"))
        return numbers



















validate_internal_phone = RegexValidator(regex = re.compile(r'^[0-9]{4}$'), \
   message = _(u"You should input 4 digits for a short number."), \
   code = 'four_digits')

class TelNumberForm(forms.ModelForm):
    class Meta:
        model = TelNumber
        fields = ['password', 'person_name', 'internal_phone']

    def __init__(self, *args, **kwargs):
        '''
        init takes billservice_account object
        '''
        self.billing_account = kwargs.pop('billing_account')
        super(TelNumberForm, self).__init__(*args, **kwargs)

    password = forms.CharField(label = _(u"Password"), min_length = 6)
    person_name = forms.CharField(min_length = 3, label = _(u"Person name"), required = False)
    internal_phone = forms.CharField(
        validators = [validate_internal_phone],
        label = _(u"Short number"), required = False,
        help_text = _(u"Must consists of 4 digits"),
        widget = forms.TextInput(
            attrs = { "maxlength": "4" },
        ),
    )

    def is_unique(self, field_name, value, error):
        if unicode(value) in map(unicode, self.billing_account.phones.values_list(field_name, flat = True)):
            raise forms.ValidationError(error)

    def clean_internal_phone(self):
        # check if such phone exists
        value = self.cleaned_data['internal_phone']
        if value:
            self.is_unique('internal_phone', value, _(u"You should select another short number - this one exists already"))
        return value

    #def clean_person_name(self):
    #    # check if such phone exists
    #    value = self.cleaned_data['person_name']
    #    self.is_unique('person_name', value, \
    #                   _(u"You should select another person name - this one exists already"))
    #    return value

class ChangeTelNumberForm(TelNumberForm):
    def is_unique(self, field_name, value, error):
        if value in self.billing_account.phones.exclude(id = self.instance.id).values_list(field_name, flat = True):
            raise forms.ValidationError(error)






def group_widget_data(groups, group_id):
    choices = [
        {
            "id": g.id,
            "name": g.name,
            "numbers": [num.get_view_name() for num in g.numbers.all()]
        } for g in groups
    ]

    settings = {
        "selected_id": group_id,
        "add_button_text": _(u"Add group")
    }

    return choices, settings


class SelectGroupAndAddWidget(forms.Select):

    def render(self, *args, **kwargs):
        import simplejson as json
        s = super(SelectGroupAndAddWidget, self).render(*args, **kwargs)
        s += '&nbsp;<a href="" class="bt bt-blue2" id="add-group-button">%s</a>\n' % unicode(self.settings.get("add_button_text", _(u"Add")))
        s += '<div id="numbers-of-selected-group"></div>\n'
        s += '<script type="text/javascript" src="/media/js/SelectGroupWidget.js"></script>\n'

        extra_addgroup_get_query = self.settings.get("extra_addgroup_get_query")
        if extra_addgroup_get_query:
            s += '<script type="text/javascript">window.extra_addgroup_get_query = "' + extra_addgroup_get_query + '";</script>\n'

        ic = json.dumps(self.initial_choices)
        s += '<script type="text/javascript">window.widget_initial_choices = eval(' + ic + '); window.selected_id=%s; Setup(); </script>\n' % \
            self.settings.get("selected_id")
        return s
        print s
    def value_from_datadict(self, data, files, name):
        res = super(SelectGroupAndAddWidget, self).value_from_datadict(data, files, name)
        self.form.fields[name].choices = list(self.form.fields[name].choices) + [(res, res)]
        return res

class SelectWithAddGroupForm(forms.Form):
    "Форма для выбора группы внутренних номеров с возможностью редактирования/добавления групп прямо на месте"

    user_groups = forms.ChoiceField(
        choices = [],

        label = _(u"Group of numbers"),
        widget = SelectGroupAndAddWidget,
    )

    def __init__(self, *args, **kwargs):
        initial_choices = kwargs.pop("choices")
        settings = kwargs.pop("settings")
        super(SelectWithAddGroupForm, self).__init__(*args, **kwargs)
        self.fields["user_groups"].widget.initial_choices = initial_choices
        self.fields["user_groups"].widget.form = self
        self.fields["user_groups"].widget.settings = settings










