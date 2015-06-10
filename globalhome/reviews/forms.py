# -*- coding=utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import Review, SECTIONS
import datetime
from django.core.exceptions import ValidationError

COMMENT_MAX_LENGTH = 3000

class FormForUser(forms.Form):
    comment = forms.CharField(label=u'Ваш отзыв', max_length=COMMENT_MAX_LENGTH,
        widget=forms.Textarea(attrs={'cols':100, 'rows':6, 'style':"resize:None;"}),
    )
        

class FormForNotAuth(forms.Form):
    name = forms.CharField(label=u'Ваше имя', max_length=100,
        widget=forms.Textarea(attrs={'cols':100, 'rows':1, 'style':"resize:None;"}),)
    email = forms.EmailField(label=u'Email адрес',
        widget=forms.Textarea(attrs={'cols':100, 'rows':1, 'style':"resize:None;"}),)
    comment = forms.CharField(label='Ваш отзыв', max_length=COMMENT_MAX_LENGTH,
        widget=forms.Textarea(attrs={'cols':100, 'rows':6, 'style':"resize:None;"}),
    )


class AdminReviewForm(forms.ModelForm):
    section = forms.ChoiceField(choices=[[key, value]for key, value in SECTIONS.items()], required=True)
    class Meta:
        model = Review
        fields = ['comment', 'is_public', 'parent', 'user', 'section']
        
    def __init__(self, *args, **kwargs):
        super(AdminReviewForm, self).__init__(*args, **kwargs)
        self.fields['parent'].required = False 


class SectionForm(forms.Form):
    section = forms.ChoiceField(choices=[[key, value]for key, value in SECTIONS.items()], label=u'Выберите раздел, к которому относится ваш отзыв',
                                widget=forms.Select(attrs={'cols':100, 'rows':2}),)
