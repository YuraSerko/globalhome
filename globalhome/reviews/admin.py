# coding: utf-8
from django.contrib import admin
from models import Review
from forms import AdminReviewForm
from django import forms
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect



class ChangeIsPublicForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    is_public = forms.ChoiceField(choices=[[True, 'Подтвердить корректность отзыва'], [False, 'Сделать невидимым отзыв']], label=u'Подтвердить/отменить видимость') 


def change_is_public(self, request, queryset):
    model = self.model
    opts = model._meta
    form = None
    print 'request.POST %s' % (request.POST)
    if 'apply' in request.POST:
        form = ChangeIsPublicForm(request.POST)
        if form.is_valid():
            is_public = form.cleaned_data['is_public']
            count = 0
            for item in queryset:
                print 'count %s' % (count)
                item.is_public = is_public
                item.save()
                count += 1
            self.message_user(request, "Поле видимость отзывов, равное %s установленно у %d микротиков." % (is_public, count))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ChangeIsPublicForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    t = loader.get_template('admin/action.html')
    c = RequestContext(request, {'items': queryset,
                                'form': form,
                                'title':u'Изменить значение видимости для пользователей',
                                'app_label': opts.app_label,
                                'hidden_input':'change_is_public',
                                'label':'Поле Видимость отзыва будет установлено для отзывов:',
                                'opts':opts,
                                 })
    return HttpResponse(t.render(c))
change_is_public.short_description = u"Изменить поле видимости"
change_is_public.allow_tags = True



class ReviewAdmin(admin.ModelAdmin):
    actions = [change_is_public]
    form = AdminReviewForm
    list_display = ['comment', 'user_name', 'parent', 'section', 'created_at', 'is_public', ]
    list_filter = ['section']
    readonly_fields = ['comment', 'user']
   
    def save_model(self, request, obj, form, change):
        if not (obj.user):
            obj.user = request.user
        obj.user_name = obj.user.username
        obj.user_email = obj.user.email
        obj.save()

    
admin.site.register(Review, ReviewAdmin)
