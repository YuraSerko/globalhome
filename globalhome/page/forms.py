from django.forms import ModelForm
from page.models import Message, LeftBlockMenuPage
from django import forms

class message_form(forms.ModelForm):

    class Meta:
        model = Message

class UploadForm(forms.Form):
    file = forms.FileField(
        label='Select a file'
        )
    
    
class PageForm(forms.ModelForm):

    class Meta:
        model = LeftBlockMenuPage
        fields = ['name', 'url', 'parent', 'position']
        
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['parent'].required = False 
   

