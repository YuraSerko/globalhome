# coding: utf-8

from lib.decorators import login_required
from job.forms import HotSpotWorkExperienceForm
from job.models import HotSpotWorkExperience
from job.models import HotSpotWorkEducationAndSkills
from job.forms import HotSpotWorkEducationAndSkillsForm
from job.models import HotSpotWorkEducationalInstitution
from job.forms import HotSpotWorkEducationalInstitutionForm
from job.models import HotSpotWorkResumes
from job.forms import HotSpotWorkForeignLanguagesProfForm
from job.models import HotSpotWorkForeignLanguagesProf

from job.models import HotSpotWorkAdditionalEducation
from job.forms import HotSpotWorkAdditionalEducationForm
from job.models import HotSpotWorkPortfolio
from job.forms import HotSpotWorkPortfolioForm
from job.models import HotSpotWorkWishes
from job.forms import HotSpotWorkWishesForm

from job.models import HotSpotSpecializations
from job.models import HotSpotWorkEmployerData
from job.forms import HotSpotWorkEmployerDataForm

from job.models import HotSpotWorkVacancies
from job.models import HotSpotWorkDutiesAndRequirements
from job.forms import HotSpotWorkDutiesAndRequirementsForm
from job.models import HotSpotWorkForeignLanguagesVacancy
from job.forms import HotSpotWorkForeignLanguagesVacancyForm
from job.models import HotSpotWorkConditions
from job.forms import HotSpotWorkConditionsForm
from job.models import HotSpotProfessions
from django.forms.models import modelformset_factory
from job.models import HotSpotCompetitorCity
from job.models import HotSpotMetroLines
from job.models import HotSpotMetroStations
from django.utils import simplejson
from job.forms import HotSpotWorkJobSeekerPersonalDataForm
from job.models import HotSpotWorkJobSeekerPersonalData
from dateutil.relativedelta import relativedelta
from page.views import panel_base_auth
from job.tasks import job_ru_register
import math

from lib.decorators import render_to, login_required_job
from django.http import HttpResponseRedirect, Http404
from billing.models import BillserviceAccount

from hotspot.views import hotspot_identity
from account.models import Profile
import datetime
from django.shortcuts import  HttpResponse
from job.models import HotSpotWorkJobRuCreated
#============================================================================================================
@login_required_job
@render_to('work_resume.html')
def work_resume(request):
    context = {}
    resume_ww_ads_dict = {}
    ids_list = []
    context['no_account'] = False
    
    # получаем юзера и HotSpotWorkJobSeekerPersonalData (experince связан по внешенему ключу)
    '''
    if request.user.is_anonymous():
        return HttpResponseRedirect('/work/need_login')
    '''
    bac = BillserviceAccount.objects.get(username=request.user.username)  
    try:
        work_personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(billservac=bac)
    except  HotSpotWorkJobSeekerPersonalData.DoesNotExist:
        context.update(hotspot_identity(request))
        context['no_account'] = True
        return context
    
    work_resume_objs = HotSpotWorkResumes.objects.filter(personal_data=work_personal_data_obj).order_by('create_date')
    for work_resume_obj in work_resume_objs:
        ids_list = []
        try:
            work_wishes_obj = HotSpotWorkWishes.objects.get(resume=work_resume_obj)
            ids_list.append(work_wishes_obj)
        except HotSpotWorkWishes.DoesNotExist:
            ids_list.append(0)
            
        try:
            work_ad_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume=work_resume_obj)
            ids_list.append(work_ad_and_skills_obj)
        except HotSpotWorkEducationAndSkills.DoesNotExist:
            ids_list.append(0)
        resume_ww_ads_dict[work_resume_obj] = ids_list
        try:
            work_jobru_created = HotSpotWorkJobRuCreated.objects.get(doc_id=work_resume_obj.id)
            ids_list.append(work_jobru_created)
        except  HotSpotWorkJobRuCreated.DoesNotExist:
            ids_list.append(0)
            
        resume_ww_ads_dict[work_resume_obj] = ids_list    
            
    context['resume_ww_ads_dict'] = resume_ww_ads_dict
    context['my_resume'] = True
    context['work_page'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return context
#============================================================================================================

@login_required_job
@render_to('work_resume_add_edit.html')
def work_resume_add_edit(request, resume_id):
    context = {}
    red_url = ''  # переход на адрес с resume id
    education_and_skills_id = 0  # id экзэмляра модели HotSpotWorkEducationAndSkills
    work_wishes_id = 0  # id экземпляра модели HotSpotWorkWishes
    context['my_resume'] = True
    context['work_page'] = True
    context['form_number'] = request.POST.get("form_number")  # для перехода на нужную форму после submit
    
    context['work_wishes_specialization_objs'] = {}
    context['work_wishes_select_specialization'] = {}
    
    # получаем юзера и HotSpotWorkJobSeekerPersonalData (experince связан по внешенему ключу)
    bac = BillserviceAccount.objects.get(username=request.user.username)  
    work_personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(billservac=bac)
   
    if resume_id != '0':
        resume_obj = HotSpotWorkResumes(id=int(resume_id))
#-------------------------------------------------------------------------------------------------------------------------------------------------
    def create_or_add_resume(resume_id, work_personal_data_obj):
        red_url = ''
        if (resume_id != '0'):
            resume_obj = HotSpotWorkResumes(id=int(resume_id))
        if (resume_id == '0'):
            # создадим объект
            resume_obj = HotSpotWorkResumes(personal_data=work_personal_data_obj)
            resume_obj.save()
            red_url = '/work_acount/resume/add_edit/' + str(resume_obj.id) + '/'
            resume_id = resume_obj.id
        return resume_obj, red_url
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    def fill_formset_experiences(work_wishes_id):
        queryset = HotSpotWorkExperience.objects.filter(work_wishes__id=work_wishes_id)
        if work_wishes_id == 0 or  queryset.count() == 0:
            HotSpotWorkExperienceFormSet = modelformset_factory(HotSpotWorkExperience, extra=1 , form=HotSpotWorkExperienceForm, can_delete=True)
            formset_experiences = HotSpotWorkExperienceFormSet(prefix='workplace', queryset=HotSpotWorkExperience.objects.none())
        else:
            HotSpotWorkExperienceFormSet = modelformset_factory(HotSpotWorkExperience, extra=0 , form=HotSpotWorkExperienceForm, can_delete=True)
            formset_experiences = HotSpotWorkExperienceFormSet(queryset=queryset, prefix='workplace')
        return formset_experiences    
#-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_form_educaton_and_skills():
        try:
            education_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume__id=int(resume_id))
            educaton_and_skills_form = HotSpotWorkEducationAndSkillsForm(instance=education_and_skills_obj)
        except HotSpotWorkEducationAndSkills.DoesNotExist:
            educaton_and_skills_form = HotSpotWorkEducationAndSkillsForm()
        return educaton_and_skills_form
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    def fill_formset_educational_institution(education_and_skills_id):
        queryset = HotSpotWorkEducationalInstitution.objects.filter(education_and_skills__id=education_and_skills_id)
        if queryset.count() == 0 or education_and_skills_id == 0:
            HotSpotWorkEducationalInstitutionFormSet = modelformset_factory(HotSpotWorkEducationalInstitution, extra=1 , form=HotSpotWorkEducationalInstitutionForm, can_delete=True)
            formset_ed_inst = HotSpotWorkEducationalInstitutionFormSet(prefix='educational_institution', queryset=HotSpotWorkEducationalInstitution.objects.none())
        else:
            HotSpotWorkEducationalInstitutionFormSet = modelformset_factory(HotSpotWorkEducationalInstitution, extra=0 , form=HotSpotWorkEducationalInstitutionForm, can_delete=True)
            formset_ed_inst = HotSpotWorkEducationalInstitutionFormSet(queryset=queryset, prefix='educational_institution')
        return formset_ed_inst    
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    def fill_formset_proficiency_language(education_and_skills_id):
        queryset = HotSpotWorkForeignLanguagesProf.objects.filter(education_and_skills__id=education_and_skills_id)
        if queryset.count() == 0  or education_and_skills_id == 0:
            HotSpotWorkForeignLanguagesProfFormSet = modelformset_factory(HotSpotWorkForeignLanguagesProf, extra=1 , form=HotSpotWorkForeignLanguagesProfForm, can_delete=True)
            formset_prof_lang = HotSpotWorkForeignLanguagesProfFormSet(prefix='proficiency_language', queryset=HotSpotWorkForeignLanguagesProf.objects.none())
        else:
            HotSpotWorkForeignLanguagesProfFormSet = modelformset_factory(HotSpotWorkForeignLanguagesProf, extra=0 , form=HotSpotWorkForeignLanguagesProfForm, can_delete=True)
            formset_prof_lang = HotSpotWorkForeignLanguagesProfFormSet(queryset=queryset, prefix='proficiency_language')
        return formset_prof_lang    
#-------------------------------------------------------------------------------------------------------------------------------------------------    
    def fill_formset_additional_education(education_and_skills_id):
        queryset = HotSpotWorkAdditionalEducation.objects.filter(education_and_skills__id=education_and_skills_id)
        if queryset.count() == 0  or education_and_skills_id == 0:
            HotSpotWorkAdditionalEducationFormSet = modelformset_factory(HotSpotWorkAdditionalEducation, extra=1 , form=HotSpotWorkAdditionalEducationForm, can_delete=True)
            formset_add_ed = HotSpotWorkAdditionalEducationFormSet(prefix='additional_education', queryset=HotSpotWorkAdditionalEducation.objects.none())
        else:
            HotSpotWorkAdditionalEducationFormSet = modelformset_factory(HotSpotWorkAdditionalEducation, extra=0 , form=HotSpotWorkAdditionalEducationForm, can_delete=True)
            formset_add_ed = HotSpotWorkAdditionalEducationFormSet(queryset=queryset, prefix='additional_education')
        return formset_add_ed    
#-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_formset_portfolio(education_and_skills_id):
        queryset = HotSpotWorkPortfolio.objects.filter(education_and_skills__id=education_and_skills_id)
        if queryset.count() == 0  or education_and_skills_id == 0:
            HotSpotWorkPortfolioFormSet = modelformset_factory(HotSpotWorkPortfolio, extra=1 , form=HotSpotWorkPortfolioForm, can_delete=True)
            formset_portfolio = HotSpotWorkPortfolioFormSet(prefix='portfolio', queryset=HotSpotWorkPortfolio.objects.none())
        else:
            HotSpotWorkPortfolioFormSet = modelformset_factory(HotSpotWorkPortfolio, extra=0 , form=HotSpotWorkPortfolioForm, can_delete=True)
            formset_portfolio = HotSpotWorkPortfolioFormSet(queryset=queryset, prefix='portfolio')
        return formset_portfolio    
#-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_form_work_wishes():
        try:
            work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=int(resume_id))
            work_wishes_form = HotSpotWorkWishesForm(instance=work_wishes_obj)
        except HotSpotWorkWishes.DoesNotExist:
            work_wishes_form = HotSpotWorkWishesForm()
        return work_wishes_form
#-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_work_wishes_spec_select():
        # беру все что есть в наличии в модели HotSpotSpecializations
        work_wishes_specialization_str = ''
        work_wishes_specializations_all = HotSpotSpecializations.objects.all().order_by('id')
        if resume_id != 0:
            try:
                # если есть HotSpotWorkWishes то есть и HotSpotSpecializations (req true)
                work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=int(resume_id))
                work_wishes_specialization_objs = work_wishes_obj.specialization.all()
                # work_wishes_specialization_str = ''
                for sp in work_wishes_specialization_objs:
                    work_wishes_specialization_str = work_wishes_specialization_str + str(sp.id) + ','
            except HotSpotWorkWishes.DoesNotExist:
                pass   
        context['work_wishes_specialization_selected'] = work_wishes_specialization_str
        context['work_wishes_select_specialization'] = work_wishes_specializations_all
#--------------------------------------------------------------------------------------------------------------------------
    if request.method == 'POST':
        #------------------------------------------------------------------------------------------------------------------   
        # HotSpotWorkEducationAndSkillsForm применяем изменения и передаем контекстом получившуюся форму
        if request.POST.has_key('education_level'):
            try:
                education_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume__id=int(resume_id))
                educaton_and_skills_form = HotSpotWorkEducationAndSkillsForm(request.POST, instance=education_and_skills_obj)
            except HotSpotWorkEducationAndSkills.DoesNotExist:
                educaton_and_skills_form = HotSpotWorkEducationAndSkillsForm(request.POST)
            if educaton_and_skills_form.is_valid():
                easf = educaton_and_skills_form.save(commit=False)
                resume_obj, red_url = create_or_add_resume(resume_id, work_personal_data_obj)
                easf.resume = resume_obj
                easf.save()
                # сохраним id объекта HotSpotWorkEducationAndSkills для передачи в formsets ниже
                education_and_skills_id = easf.id
            else:
                raise Http404
        # в любом случае если был любойPOST берем данные из БД
        educaton_and_skills_form_context = fill_form_educaton_and_skills()           
        # '''''''''''''''''''''''''''''''''''''''''''''''''''
        # FORMSET HotSpotWorkEducationalInstitutionFormSet
        if request.POST.has_key('educational_institution-TOTAL_FORMS'):
            deleted_form_edinst = ''
            HotSpotWorkEducationalInstitutionFormSet = modelformset_factory(HotSpotWorkEducationalInstitution, extra=0, form=HotSpotWorkEducationalInstitutionForm, can_delete=True)
            formset_edinst = HotSpotWorkEducationalInstitutionFormSet(request.POST.copy(), request.FILES, prefix='educational_institution')
            for form_edinst in formset_edinst:
                if form_edinst.is_valid():
                    try:
                        deleted_form_edinst = form_edinst.cleaned_data['deleted']
                    except:
                        pass
                    edinst = form_edinst.save(commit=False)
                    edinst.education_and_skills = HotSpotWorkEducationAndSkills.objects.get(id=education_and_skills_id)
                    edinst.save()
                    if deleted_form_edinst == True:
                        hswei = HotSpotWorkEducationalInstitution.objects.get(id=edinst.id)
                        hswei.delete()
                else:
                    raise Http404
                    
        educational_instutions_form_context = fill_formset_educational_institution(education_and_skills_id) 
 
        # '''''''''''''''''''''''''''''''''''''''''''''''''''
        # FORMSET HotSpotWorkForeignLanguagesProfFormSet
        if request.POST.has_key('proficiency_language-TOTAL_FORMS'):
            HotSpotWorkForeignLanguagesProfFormSet = modelformset_factory(HotSpotWorkForeignLanguagesProf, extra=0, form=HotSpotWorkForeignLanguagesProfForm, can_delete=True)
            formset_proficiency_language = HotSpotWorkForeignLanguagesProfFormSet(request.POST.copy(), request.FILES, prefix='proficiency_language')
            for form_proficiency_language in formset_proficiency_language:
                if form_proficiency_language.is_valid():
                    deleted_form_prof_lang = ''
                    lang_obj = False
                    no_lang_on_form = False
                    # если поля пустые
                    try:
                        if form_proficiency_language.cleaned_data['language'] == None and form_proficiency_language.cleaned_data['proficiency_language_level'] == None:
                            no_lang_on_form = True
                    except:
                        pass
                    if form_proficiency_language.cleaned_data == {}:
                        no_lang_on_form = True    
                    # если объект в базе и помечен на удалеление 
                    try:
                        deleted_form_prof_lang = form_proficiency_language.cleaned_data['deleted']
                    except:
                        pass
                    form_proficiency_languagecf = form_proficiency_language.save(commit=False)
                    # если объект в базе
                    if form_proficiency_languagecf.id != None:
                        lang_obj = True
                    form_proficiency_languagecf.education_and_skills = HotSpotWorkEducationAndSkills.objects.get(id=education_and_skills_id)
                    # если оба поля не пустые сохраняем объект
                    if no_lang_on_form == False:
                        form_proficiency_languagecf.save()
                    # если помечен на удаление или есть объект и оба поля пустые то удаляем
                    if deleted_form_prof_lang == True or (lang_obj == True and  no_lang_on_form == True):
                        hswflp = HotSpotWorkForeignLanguagesProf.objects.get(id=form_proficiency_languagecf.id)
                        hswflp.delete()
                else:
                    raise Http404  
        proficiency_language_form_context = fill_formset_proficiency_language(education_and_skills_id) 
        # '''''''''''''''''''''''''''''''''''''''''''''''''   
        # FORMSET HotSpotWorkAdditionalEducationFormSet
        if request.POST.has_key('additional_education-TOTAL_FORMS'):
            HotSpotWorkAdditionalEducationFormSet = modelformset_factory(HotSpotWorkAdditionalEducation, extra=0, form=HotSpotWorkAdditionalEducationForm, can_delete=True)
            formset_additional_education = HotSpotWorkAdditionalEducationFormSet(request.POST.copy(), request.FILES, prefix='additional_education')
            for form_additional_education in formset_additional_education:
                if form_additional_education.is_valid():
                    deleted_form_added = ''
                    aded_obj = False
                    no_aded_on_form = False
                    # ---если поля пустые
                    try:
                        if form_additional_education.cleaned_data['institution_name'] == '' and form_additional_education.cleaned_data['course_name'] == '' and form_additional_education.cleaned_data['graduate_year_ad'] == None:
                            no_aded_on_form = True
                    except:
                        pass
                    if form_additional_education.cleaned_data == {}:
                        no_aded_on_form = True
                    #-----        
                    try:
                        deleted_form_added = form_additional_education.cleaned_data['deleted']
                    except:
                        pass
                    form_additional_educationcf = form_additional_education.save(commit=False)
                    # если объект в базе
                    if form_additional_educationcf.id != None:
                        aded_obj = True
                    form_additional_educationcf.education_and_skills = HotSpotWorkEducationAndSkills.objects.get(id=education_and_skills_id)
                    if no_aded_on_form == False:
                        form_additional_educationcf.save()
                    if deleted_form_added == True or (aded_obj == True and  no_aded_on_form == True):
                        hswae = HotSpotWorkAdditionalEducation.objects.get(id=form_additional_educationcf.id)
                        hswae.delete()
                else:
                    raise Http404 
        additional_education_formset_context = fill_formset_additional_education(education_and_skills_id) 
        # '''''''''''''''''''''''''''''''''''''''''''''''''    
        # FORMSET HotSpotWorkPortfolioFormSet
        if request.POST.has_key('portfolio-TOTAL_FORMS'):
            HotSpotWorkPortfolioFormSet = modelformset_factory(HotSpotWorkPortfolio, extra=0, form=HotSpotWorkPortfolioForm, can_delete=True)
            formset_portfolio = HotSpotWorkPortfolioFormSet(request.POST.copy(), request.FILES, prefix='portfolio')
            for form_portfolio in formset_portfolio:
                if form_portfolio.is_valid():
                    deleted_form_portfolio = ''
                    port_obj = False
                    no_port_on_form = False
                    # если поле пустое
                    try:
                        if form_portfolio.cleaned_data['portfolio_link'] == '':
                            no_port_on_form = True
                    except:
                        pass
                    if form_portfolio.cleaned_data == {}:
                        no_port_on_form = True
                    #------
                    try:
                        deleted_form_portfolio = form_portfolio.cleaned_data['deleted']
                    except:
                        pass
                    form_portfoliocf = form_portfolio.save(commit=False)
                    # если объект в базе
                    if form_portfoliocf.id != None:
                        port_obj = True
                    form_portfoliocf.education_and_skills = HotSpotWorkEducationAndSkills.objects.get(id=education_and_skills_id)
                    if no_port_on_form == False:
                        form_portfoliocf.save()
                    if deleted_form_portfolio == True or (port_obj == True and  no_port_on_form == True):
                        hswp = HotSpotWorkPortfolio.objects.get(id=form_portfoliocf.id)
                        hswp.delete()
                else:
                    raise Http404 
        portfolio_formset_context = fill_formset_portfolio(education_and_skills_id) 
        # '''''''''''''''''''''''''''''''''''''''''''''''''   
        #------------------------------------------------------------------------------------------------------------------
        # HotSpotWorkWishesForm применяем изменения и передаем контекстом получившуюся форму
        if request.POST.has_key('desirable_position'):
            try:
                work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=int(resume_id))
                work_wishes_form = HotSpotWorkWishesForm(request.POST, instance=work_wishes_obj)
            except HotSpotWorkWishes.DoesNotExist:
                work_wishes_form = HotSpotWorkWishesForm(request.POST)
            if work_wishes_form.is_valid():
                work_wishes_formcf = work_wishes_form.save(commit=False)
                resume_obj, red_url = create_or_add_resume(resume_id, work_personal_data_obj)
                work_wishes_formcf.resume = resume_obj
                work_wishes_formcf.save()
                work_wishes_id = work_wishes_formcf.id
                work_wishes_form.save_m2m()
            else:
                raise Http404   
            
        # в любом случае если был любойPOST берем данные из БД
        work_wishes_form_context = fill_form_work_wishes()          
        #------------------------------------------------------------------------------------------------------------------ 
        # FORMSET HotSpotWorkExperienceFormSet
        deleted_form_exp = ''
        if request.POST.has_key('workplace-TOTAL_FORMS'):
            HotSpotWorkExperienceFormSet = modelformset_factory(HotSpotWorkExperience, extra=0, form=HotSpotWorkExperienceForm, can_delete=True)
            formset_experiences = HotSpotWorkExperienceFormSet(request.POST, request.FILES, prefix='workplace')
            for form_exp in formset_experiences:
                if form_exp.is_valid():
                    try:
                        deleted_form_exp = form_exp.cleaned_data['deleted']
                    except:
                        pass
                    fe = form_exp.save(commit=False)
                    fe.work_wishes = HotSpotWorkWishes.objects.get(id=work_wishes_id)
                    if deleted_form_exp == True:
                        try:
                            hswe = HotSpotWorkExperience.objects.get(id=fe.id)
                            hswe.delete()
                        except HotSpotWorkExperience.DoesNotExist:
                            pass
                    else:
                        fe.save()
                else:
                    raise Http404 
        # в любом случае если был любойPOST берем данные из БД
        formset_experiences_context = fill_formset_experiences(work_wishes_id) 
                
        # get education_and_skills_id
        if resume_id != 0:
            try:
                education_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume__id=resume_id)
                education_and_skills_id = education_and_skills_obj.id
            except HotSpotWorkEducationAndSkills.DoesNotExist:
                pass
            try:
                work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=resume_id)
                work_wishes_id = work_wishes_obj.id
            except HotSpotWorkWishes.DoesNotExist:
                pass
        # поле с группировкой work wishes spec select
        fill_work_wishes_spec_select()  
        #------------------------------------------------------------------------------------------------------------------
        if red_url != '':  # потом в самый конец
            return HttpResponseRedirect(red_url)
    else:  # NOT POST
        
        # HotSpotWorkEducationAndSkillsForm
        educaton_and_skills_form_context = fill_form_educaton_and_skills()
        
        # get education_and_skills_id
        if resume_id != 0:
            try:
                education_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume__id=resume_id)
                education_and_skills_id = education_and_skills_obj.id
            except HotSpotWorkEducationAndSkills.DoesNotExist:
                pass
            try:
                work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=resume_id)
                work_wishes_id = work_wishes_obj.id
            except HotSpotWorkWishes.DoesNotExist:
                pass
        # HotSpotWorkEducationalInstitutionFormSet
        educational_instutions_form_context = fill_formset_educational_institution(education_and_skills_id) 
        
        # HotSpotWorkEducationalInstitutionFormSet
        proficiency_language_form_context = fill_formset_proficiency_language(education_and_skills_id) 
        
        # FORMSET HotSpotWorkAdditionalEducationFormSet
        additional_education_formset_context = fill_formset_additional_education(education_and_skills_id)
        
        # FORMSET HotSpotWorkPortfolioFormSet
        portfolio_formset_context = fill_formset_portfolio(education_and_skills_id) 
        
        # HotSpotWorkExperienceFormSet
        formset_experiences_context = fill_formset_experiences(work_wishes_id)
        
        # HotSpotWorkWishesForm
        work_wishes_form_context = fill_form_work_wishes()
                
        # поле с группировкой work wishes spec select
        fill_work_wishes_spec_select()
        
    # передаем все формы в контекст
    context["formset_experiences"] = formset_experiences_context
    context["educaton_and_skills_form"] = educaton_and_skills_form_context
    context["formset_educational_institution"] = educational_instutions_form_context
    context["formset_proficiency_language"] = proficiency_language_form_context
    context['formset_additional_education'] = additional_education_formset_context
    context['formset_portfolio'] = portfolio_formset_context
    context['form_work_wishes'] = work_wishes_form_context
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return context
#============================================================================================================
# тип эккаунта
@login_required_job
def work_account_type(request, context):
    work_logged = False
    is_employer = ''
    if request.user.is_authenticated():  # если юзер залогинен
        work_logged = True
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.is_juridical:
            is_employer = True
        else:
            is_employer = False
    except:
        pass   
    context['work_logged'] = work_logged
    context['is_employer'] = is_employer 
#============================================================================================================
@render_to('work.html')
def work(request):
    context = {}

    res_dict_vac = {}
    res_list_vac = []
    res_dict_resume = {}
    res_list_resume = []
    context['work_page'] = True
    
    # три последние вакансии
    vac_objs = HotSpotWorkVacancies.objects.filter(publication_date__isnull=False).order_by('-publication_date')[:3]
    i = 1
    for vac_obj in vac_objs:
        duties_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy=vac_obj)
        cond_obj = HotSpotWorkConditions.objects.get(duties_and_req=duties_obj)
        res_list_vac = [vac_obj.id, duties_obj.vacancy_name.profession,
                   vac_obj.employer_data.company_name,
                   vac_obj.employer_data.get_ownership_form_display(),
                   cond_obj.salary_from, cond_obj.salary_to,
                   vac_obj.publication_date, cond_obj.city ]
        res_dict_vac[i] = res_list_vac
        i = i + 1
    
    # три последних резюме
    resume_objs = HotSpotWorkResumes.objects.filter(publication_date__isnull=False).order_by('-publication_date')[:3]
    j = 1
    for resume_obj in resume_objs:
        wishes_obj = HotSpotWorkWishes.objects.get(resume=resume_obj)
        
        # сформировать строку возраст+пол+город
        NOW = datetime.datetime.now()
        sex = resume_obj.personal_data.get_sex_display()
        birthday = resume_obj.personal_data.birthday
        rel = relativedelta(NOW, birthday)
        age = rel.years
        if  15 < age < 69:
            age_str = kwagedict[age]
        else:
            age_str = u'лет'
        private_string = sex + ',' + str(age) + ' ' + age_str  
        # list
        res_list_resume = [resume_obj.id, wishes_obj.desirable_position.profession,
                            private_string, wishes_obj.salary,
                             wishes_obj.get_salary_um_display() ,
                             resume_obj.personal_data.living_city.city,
                             resume_obj.publication_date]
        res_dict_resume[j] = res_list_resume
        j = j + 1
    context['res_dict_vac'] = res_dict_vac
    context['res_dict_resume'] = res_dict_resume
    work_account_type(request, context)
    return panel_base_auth(request, context)
   

#=============================================================================================================
@login_required_job
@render_to('work_personal_data.html')
def work_perosanl_data(request):
    context = {}
    bac = BillserviceAccount.objects.get(username=request.user.username)      
    def fill_form_work_personal_data():
        metro_stations_str = ''
        selected_station = None
        try:
            work_personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(billservac=bac)
            data = {'ID':work_personal_data_obj.id}
            form = HotSpotWorkJobSeekerPersonalDataForm(instance=work_personal_data_obj)
            # living_city обязательное поле - если есть linving city нужно проверять наличие у города метро
            metro_stations = HotSpotMetroStations.objects.filter(line__city_id=work_personal_data_obj.living_city.id)
            # есть ли выбранная станция
            if metro_stations.count() != 0:
                if work_personal_data_obj.metro_station != None:
                        selected_station = work_personal_data_obj.metro_station.id
            if metro_stations.count() != 0:
                # формируем начало select если  нет выбранной станции первый пункт selected
                if selected_station == None:
                    metro_stations_str = '<option value="" selected="selected">---------</option>'
                else:
                    metro_stations_str = '<option value="">---------</option>'
                # формируем строку для select    
                for ms in metro_stations:
                    if selected_station == None:
                        metro_stations_str = metro_stations_str + '<option value=' + str(ms.id) + '>' + ms.station + '(' + ms.line.line + ')' + '</option>'
                    else:
                        if selected_station == ms.id:
                            metro_stations_str = metro_stations_str + '<option value=' + str(ms.id) + ' selected="selected">' + ms.station + '(' + ms.line.line + ')' + '</option>'
                        else:
                            metro_stations_str = metro_stations_str + '<option value=' + str(ms.id) + '>' + ms.station + '(' + ms.line.line + ')' + '</option>'
            # если станций не было то делаем selected без value
            if metro_stations_str == '':
                metro_stations_str = '<option value="" selected="selected">---------</option>'
            
        except HotSpotWorkJobSeekerPersonalData.DoesNotExist:
            form = HotSpotWorkJobSeekerPersonalDataForm()
            # если нет записей в базе
            if metro_stations_str == '':
                metro_stations_str = '<option value="" selected="selected">---------</option>'
        return form, metro_stations_str
    if request.POST:
        try:
            work_personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(billservac=bac)
            form = HotSpotWorkJobSeekerPersonalDataForm(request.POST, request.FILES, instance=work_personal_data_obj)
            if form.is_valid():
                form.save()
            else:
                raise Http404  
        except HotSpotWorkJobSeekerPersonalData.DoesNotExist:
            form = HotSpotWorkJobSeekerPersonalDataForm(request.POST, request.FILES)
            if form.is_valid():
                wor = form.save(commit=False)
                wor.billservac = bac 
                wor.save()
            else:
                raise Http404    
        form, metro_stations_str = fill_form_work_personal_data()
        context['metro_stations'] = metro_stations_str 
    else:
        form, metro_stations_str = fill_form_work_personal_data()
        context['metro_stations'] = metro_stations_str   

    context['form'] = form  
    context['work_page'] = True
    context['personal_data'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return context

#=========================================================================================================
@login_required_job
def ajax_work_metro_city_change(request):
    result_str = ''
    if request.POST.has_key('city_id'):
        city_id = request.POST.get('city_id')
        metro_stations = HotSpotMetroStations.objects.filter(line__city_id=city_id)
        result_str = ''
        if metro_stations.count() > 0:
            result_str = '<option value="" selected="selected">---------</option>'
        for ms in metro_stations:
            result_str = result_str + '<option value=' + str(ms.id) + '>' + ms.station + '(' + ms.line.line + ')' + '</option>'
        return HttpResponse(result_str)
    else:
        return HttpResponse(result_str)

#=========================================================================================================
@login_required_job
def work_delete_photo(request):
    personal_data_id = request.POST.get('obj_id')
    personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(id=int(personal_data_id))
    personal_data_obj.photo.delete()
    personal_data_obj.photo = 'uploads/work_photo/None/no-img.jpg'
    personal_data_obj.save()
    return HttpResponse('1')   
#==================================================================================================================
@login_required_job
@render_to('work_employer_data.html')
def work_employer_data(request):
    context = {}
    bac = BillserviceAccount.objects.get(username=request.user.username)  # !!!! юзер всгда залогинен
    
    def fill_work_employer_data_form():
        try:
            work_emloyer_data = HotSpotWorkEmployerData.objects.get(billservac=bac)
            form = HotSpotWorkEmployerDataForm(instance=work_emloyer_data) 
        except HotSpotWorkEmployerData.DoesNotExist:
            form = HotSpotWorkEmployerDataForm()
        return form
    
    if request.POST:  # есть post
        try:
            work_emloyer_data = HotSpotWorkEmployerData.objects.get(billservac=bac)
            form = HotSpotWorkEmployerDataForm(request.POST, instance=work_emloyer_data)
            if form.is_valid():
                form.save()
            else:
                raise Http404 
        except HotSpotWorkEmployerData.DoesNotExist:
            form = HotSpotWorkEmployerDataForm(request.POST)
            if form.is_valid:
                wor = form.save(commit=False)
                wor.billservac = bac 
                wor.save()
            else:
                raise Http404    
    form = fill_work_employer_data_form()  # независимо есть post или нет

    context['form'] = form
    context['work_page'] = True
    context['work_eployer_data'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return panel_base_auth(request, context)  # return context original
#==================================================================================================================
@login_required_job
@render_to('work_vacancy.html')
def work_vacancy(request):
    context = {}
    context['work_page'] = True
    work_vacancy_dut_cond = {}
    ids_list = []
    context['no_vacancy'] = False
    
    # получаем юзера и HotSpotWorkEmployerData 
    if request.user.is_anonymous():
        return HttpResponseRedirect('/work/need_login')
    bac = BillserviceAccount.objects.get(username=request.user.username)  # !!!! юзер всгда залогинен
    try:
        work_employer_data_obj = HotSpotWorkEmployerData.objects.get(billservac=bac)
    except HotSpotWorkEmployerData.DoesNotExist:
        context.update(hotspot_identity(request))
        context['no_vacancy'] = True
        return context
    work_vacancy_objs = HotSpotWorkVacancies.objects.filter(employer_data=work_employer_data_obj)
    for work_vacancy_obj in work_vacancy_objs:
        ids_list = []
        work_dut_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy=work_vacancy_obj)
        ids_list.append(work_dut_obj)
        try:
            work_cond = HotSpotWorkConditions.objects.get(duties_and_req=work_dut_obj)
            ids_list.append(work_cond)
        except HotSpotWorkConditions.DoesNotExist:
            ids_list.append(0)
        work_vacancy_dut_cond[work_vacancy_obj] = ids_list
    context['work_vacancy_list'] = True
    context['work_vacancy_objs'] = work_vacancy_objs
    context['work_vacancy_dut_cond'] = work_vacancy_dut_cond
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return context
#============================================================================================================
@login_required_job
@render_to('work_vacancy_add_edit.html')
def work_vacancy_add_edit(request, vacancy_id):
    context = {}
    red_url = ''
    work_duties_and_req_id = 0
    context['duties_and_req_select_specialization'] = {}
    context['form_number'] = request.POST.get("form_number")  # для перехода на нужну форму после submit
    bac = BillserviceAccount.objects.get(username=request.user.username)  # !!!! юзер всгда залогинен
    work_employer_data_obj = HotSpotWorkEmployerData.objects.get(billservac=bac)
    #-----------------------------------------------------------------------------
    def create_or_add_vacancy(vacancy_id, work_employer_data_obj):
        red_url = ''
        if (vacancy_id != '0'):
            vacancy_obj = HotSpotWorkVacancies(id=int(vacancy_id))
        if (vacancy_id == '0'):
            # создадим объект
            vacancy_obj = HotSpotWorkVacancies(employer_data=work_employer_data_obj)
            vacancy_obj.save()
            red_url = '/work_acount/vacancy/add_edit/' + str(vacancy_obj.id) + '/'
            vacancy_id = vacancy_obj.id
        return vacancy_obj, red_url
    #-----------------------------------------------------------------------------   
    def fill_form_duties_and_requirements():
        try:
            duties_and_requirements_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy__id=int(vacancy_id))
            duties_and_req_form = HotSpotWorkDutiesAndRequirementsForm(instance=duties_and_requirements_obj)
        except HotSpotWorkDutiesAndRequirements.DoesNotExist:
            duties_and_req_form = HotSpotWorkDutiesAndRequirementsForm()
        return duties_and_req_form
    #------------------------------------------------------------------------------------------------------------------------------------------------- 
    def fill_formset_vacancy_languages(work_duties_and_req_id):
        queryset = HotSpotWorkForeignLanguagesVacancy.objects.filter(duties_and_req__id=work_duties_and_req_id)
        if queryset.count() == 0 or work_duties_and_req_id == 0:
            HotSpotWorkForeignLanguagesVacancyFormSet = modelformset_factory(HotSpotWorkForeignLanguagesVacancy, extra=1 , form=HotSpotWorkForeignLanguagesVacancyForm, can_delete=True)
            formset_vac_lan = HotSpotWorkForeignLanguagesVacancyFormSet(prefix='vac_lan', queryset=HotSpotWorkForeignLanguagesVacancy.objects.none())
        else:
            HotSpotWorkForeignLanguagesVacancyFormSet = modelformset_factory(HotSpotWorkForeignLanguagesVacancy, extra=0 , form=HotSpotWorkForeignLanguagesVacancyForm, can_delete=True)
            formset_vac_lan = HotSpotWorkForeignLanguagesVacancyFormSet(queryset=queryset, prefix='vac_lan')
        return formset_vac_lan  
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_form_condition():
        try:
            condition_obj = HotSpotWorkConditions.objects.get(duties_and_req__vacancy_id=vacancy_id)
            condition_form = HotSpotWorkConditionsForm(instance=condition_obj)
        except HotSpotWorkConditions.DoesNotExist:
            condition_form = HotSpotWorkConditionsForm()
        return condition_form
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def fill_work_duties_and_req_spec_select():
        # беру все что есть в наличии в модели HotSpotSpecializations
        duties_and_req_specialization_str = ''
        duties_and_req_specializations_all = HotSpotSpecializations.objects.all().order_by('id')
        if vacancy_id != 0:
            try:
                duties_and_req_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy__id=int(vacancy_id))
                work_duties_and_req_specialization_objs = duties_and_req_obj.activity.all()
                for sp in work_duties_and_req_specialization_objs:
                    duties_and_req_specialization_str = duties_and_req_specialization_str + str(sp.id) + ','
            except HotSpotWorkDutiesAndRequirements.DoesNotExist:
                pass 
        context['duties_and_req_specialization_selected'] = duties_and_req_specialization_str
        context['duties_and_req_select_specialization'] = duties_and_req_specializations_all
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    if request.POST:
    # HotSpotWorkDutiesAndRequirementsForm применяем изменения и передаем контекстом получившуюся форму
        if request.POST.has_key('vacancy_name'):
            try:
                work_duties_and_req_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy__id=int(vacancy_id))
                work_duties_and_req_form = HotSpotWorkDutiesAndRequirementsForm(request.POST, instance=work_duties_and_req_obj)
            except HotSpotWorkDutiesAndRequirements.DoesNotExist:
                work_duties_and_req_form = HotSpotWorkDutiesAndRequirementsForm(request.POST)
            if work_duties_and_req_form.is_valid():
                work_duties_and_req_formcf = work_duties_and_req_form.save(commit=False)
                vacancy_obj, red_url = create_or_add_vacancy(vacancy_id, work_employer_data_obj)
                work_duties_and_req_formcf.vacancy = vacancy_obj
                work_duties_and_req_formcf.save()
                work_duties_and_req_form.save_m2m()
                # сохраним id объекта HotSpotWorkEducationAndSkills для передачи в formsets ниже
                work_duties_and_req_id = work_duties_and_req_formcf.id
            else:
                raise Http404 
        # в любом случае если был любойPOST берем данные из БД
        work_duties_and_req_form_context = fill_form_duties_and_requirements()
        
        # '''''''''''''''''''''''''''''''''''''''''''''''''    
        # FORMSET HotSpotWorkForeignLanguagesVacancyFormSet
        if request.POST.has_key('vac_lan-TOTAL_FORMS'):
            # deleted_form_vac_lan = ''
            HotSpotWorkForeignLanguagesVacancyFormSet = modelformset_factory(HotSpotWorkForeignLanguagesVacancy, extra=0, form=HotSpotWorkForeignLanguagesVacancyForm, can_delete=True)
            formset_vac_lan = HotSpotWorkForeignLanguagesVacancyFormSet(request.POST, prefix='vac_lan')
            for form_vac_lan in formset_vac_lan:
                if form_vac_lan.is_valid():
                    deleted_form_vac_lan = ''
                    vac_lan_obj = False
                    no_vac_lan_on_form = False
                    # ---если поля пустые
                    try:
                        if form_vac_lan.cleaned_data['language'] == None and form_vac_lan.cleaned_data['proficiency_language_level'] == None:
                            no_vac_lan_on_form = True
                    except:
                        pass
                    if form_vac_lan.cleaned_data == {}:
                        no_vac_lan_on_form = True
                    #-----        
                    try:
                        deleted_form_vac_lan = form_vac_lan.cleaned_data['deleted']
                    except:
                        pass
                    form_vac_lancf = form_vac_lan.save(commit=False)
                    # если объект в базе
                    if form_vac_lancf.id != None:
                        vac_lan_obj = True
                    form_vac_lancf.duties_and_req = HotSpotWorkDutiesAndRequirements.objects.get(id=work_duties_and_req_id)
                    if no_vac_lan_on_form == False:
                        form_vac_lancf.save()
                    # если помечен на удаление или есть объект и оба поля пустые то удаляем
                    if deleted_form_vac_lan == True or (vac_lan_obj == True and  no_vac_lan_on_form == True):
                        hswfl = HotSpotWorkForeignLanguagesVacancy.objects.get(id=form_vac_lancf.id)
                        hswfl.delete()
                else:
                    raise Http404 
        vac_lan_formset_context = fill_formset_vacancy_languages(work_duties_and_req_id) 
        # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''   
        if request.POST.has_key('salary_from'):
            try:
                work_condition_obj = HotSpotWorkConditions.objects.get(duties_and_req__vacancy_id=vacancy_id)
                work_condition_form = HotSpotWorkConditionsForm(request.POST, instance=work_condition_obj)
            except HotSpotWorkConditions.DoesNotExist:
                work_condition_form = HotSpotWorkConditionsForm(request.POST)
              
            if work_condition_form.is_valid():
                work_condition_formcf = work_condition_form.save(commit=False)
                work_condition_formcf.duties_and_req = HotSpotWorkDutiesAndRequirements.objects.get(vacancy_id=vacancy_id)
                work_condition_formcf.save()  
        condition_form_context = fill_form_condition()       
        fill_work_duties_and_req_spec_select()
        # '''''''''''''''''''''''''''''''''''''''''''''''''        
        if red_url != '':  # потом в самый конец
            return HttpResponseRedirect(red_url)
        
    else:  # NOT POST
        if vacancy_id != 0:
            try:
                work_duties_and_req_obj = HotSpotWorkDutiesAndRequirements.objects.get(vacancy__id=vacancy_id)
                work_duties_and_req_id = work_duties_and_req_obj.id
            except HotSpotWorkDutiesAndRequirements.DoesNotExist:
                pass
            
        work_duties_and_req_form_context = fill_form_duties_and_requirements()  
        vac_lan_formset_context = fill_formset_vacancy_languages(work_duties_and_req_id) 
        condition_form_context = fill_form_condition()
        fill_work_duties_and_req_spec_select()                        
    
    context['condition_form'] = condition_form_context
    context['vac_lan_formset'] = vac_lan_formset_context
    context['duties_and_req_form'] = work_duties_and_req_form_context
    context['work_vacancy_list'] = True
    context['work_page'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return context

#---------------------------------------------------------------------------------------------------------------------
kwagedict = { 1:u'год', 2:u'года', 3:u'года', 4:u'года',
                 5:u'лет', 6:u'лет', 7:u'лет', 8:u'лет',
                 9:u'лет', 10:u'лет', 11:u'лет', 12:u'лет',
                 13:u'лет',
                 14:u'лет', 15:u'лет', 16:u'лет', 17:u'лет',
                 18:u'лет', 19:u'лет', 20:u'лет', 21:u'год',
                 22:u'года', 23:u'года', 24:u'года', 25:u'лет',
                 26:u'лет', 27:u'лет', 28:u'лет', 29:u'лет',
                 30:u'лет', 31:u'год', 32:u'года', 33:u'года',
                 34:u'года', 35:u'лет', 36:u'лет', 37:u'лет',
                 38:u'лет', 39:u'лет', 40:u'лет', 41:u'год',
                 42:u'года', 43:u'года', 44:u'года', 45:u'лет',
                 46:u'лет', 47:u'лет', 48:u'лет', 49:u'лет',
                 50:u'лет', 51:u'год', 52:u'года', 53:u'года',
                 54:u'года', 55:u'лет', 56:u'лет', 57:u'лет',
                 58:u'лет', 59:u'лет', 60:u'лет', 61:u'год',
                 62:u'года', 63:u'года', 64:u'года', 65:u'лет',
                 66:u'лет', 67:u'лет', 68:u'лет', 69:u'лет',
                 70:u'лет',
                  }
kwmonthdict = {1:u'месяц', 2: u'месяца', 3:u'месяцa', 4: u'месяца',
                   5:u'месяцев', 6: u'месяцев', 7:u'месяцев', 8: u'месяцев',
                   9:u'месяцев', 10: u'месяцев', 11:u'месяцев', 12: u'месяцев',
                   } 
kwplacedict = {1:u'место', 2:u'места', 3:u'места',
               4:u'места', 5:u'мест', 6:u'мест',
               7:u'мест', 8:u'мест', 9:u'мест',
               10:u'мест', 11:u'мест', 12:u'мест', }
#----------------------------------------------------------------------------------------------------------------------
@render_to('work_resume_search.html')
def work_resume_search(request):
    context = {}
    resume_personal_data = {}
    resume_now_data = {}
    resume_then_data = {}
    resume_all_data = {}
    work_wishes = []
    pr_id = 0
    select_resume = HotSpotProfessions.objects.all()
    
    resumes = HotSpotWorkResumes.objects.filter(publication_date__isnull=False).order_by('-publication_date')
    if request.POST.get("profession_id") != None and request.POST.get("profession_id") != '':
        pr_id = request.POST.get("profession_id")
        prof_obj = HotSpotProfessions.objects.get(id=pr_id)
        work_wishes = HotSpotWorkWishes.objects.filter(desirable_position=prof_obj, resume__publication_date__isnull=False).order_by('-resume__publication_date')
    else:
        work_wishes = HotSpotWorkWishes.objects.filter(resume__publication_date__isnull=False).order_by('-resume__publication_date')

    def calculate_date(end, start, null_value):
        date_str = ''
        working_time = relativedelta(end, start)
        w_year = False
        if  working_time.years != 0:
            if working_time.years < 69:
                date_str = date_str + str(working_time.years) + ' ' + kwagedict[math.fabs(working_time.years)]
            else:
                date_str = date_str + str(working_time.years) + u' лет' 
            w_year = True
        if  working_time.months != 0:
            if w_year == True:
                date_str = date_str + u' и ' + str(working_time.months) + ' ' + kwmonthdict[math.fabs(working_time.months)]
            else:
                date_str = date_str + str(working_time.months) + kwmonthdict[math.fabs(working_time.months)]
        if working_time.months == 0 and working_time.years == 0:
            date_str = null_value
        return date_str
        
    # формируем строку персональных данных для каждого резюме
    for resume in  resumes:
        res_string = ''
        sex = resume.personal_data.get_sex_display()
        # находим уровень образования
        ed_obj = HotSpotWorkEducationAndSkills.objects.get(resume__id=resume.id)
        ed_lev = ed_obj.get_education_level_display()
        city = resume.personal_data.living_city.city_full_name
        citship = resume.personal_data.citizenship.nationality

        NOW = datetime.datetime.now()
        # TODAY = datetime.date.today()
        birthday = resume.personal_data.birthday
        rel = relativedelta(NOW, birthday)
        age = rel.years

        if  15 < age < 69:
            age_str = kwagedict[age]
        else:
            age_str = u'лет'
        res_string = sex + ',' + str(age) + ' ' + age_str + ', ' + ed_lev + u', г. ' + city + u', гр. ' + citship
        resume_personal_data[resume.id] = res_string   
        # окончание формирования строки персональных данных
        
        # формируем блок now
        # ищем все места работы по каждому резюме если есть с открытой датой то сохряем
        open_date_work_place = False
        work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=resume.id)
        exp_objs = HotSpotWorkExperience.objects.filter(work_wishes__id=work_wishes_obj.id)
        for exp_obj in exp_objs:
            # если есть место работы с открытой датой
            if exp_obj.work_end_date == None:
                open_date_work_place = True
                resume_now_data_str = ''
                date_str = ''
                prof = exp_obj.position.profession
                
                # date
                date_str = calculate_date(NOW, exp_obj.work_start_date, u'c этого месяца')
                resume_now_data_str = '<b>' + prof + '</b><p>' + ' ' + date_str + ', ' + exp_obj.org_name
                resume_now_data[resume.id] = resume_now_data_str
            # окончание места работы с открытой датой
        if open_date_work_place == False:  # нет мест работы с открытой датой по данному резюме
            date_end_list = []
            for exp_obj in exp_objs:
                # все даты окончания в список 
                date_end_list.append(exp_obj.work_end_date)
            # если список не пустой находим последнюю
            if date_end_list != []:
                last_date_end = max(date_end_list)
                #---------------------------------------
                date_str = calculate_date(NOW, last_date_end, u'c этого месяца')
                #---------------------------------------
                resume_now_data[resume.id] = u'<b>Без работы </b>' + date_str
            else:
                resume_now_data[resume.id] = u'<b>Без опыта работы </b>'                  
        # окончание формирования блока now
        
        # блок ранее
        if exp_objs.count() > 0:
            then_work_date_list = {}
            # словарь дата exp id где нет открытой даты
            for exp_obj in exp_objs:
                if exp_obj.work_end_date != None:
                    then_work_date_list[exp_obj.work_end_date] = exp_obj.id
            
            # находим последнюю дату в словааре
            if then_work_date_list != {}:
                keys = then_work_date_list.keys()
                key = max(keys)
                exp_id = then_work_date_list[key]
                exp_then = HotSpotWorkExperience.objects.get(id=exp_id)
                # посчитаем время работы на ранее месте
                date_str = calculate_date(exp_then.work_end_date, exp_then.work_start_date, u'c этого месяца')
                #----
                resume_then_data_str = '<b>' + exp_then.position.profession + '</b>' + '<p>' + date_str + ', ' + exp_then.org_name
                resume_then_data[resume.id] = resume_then_data_str
            else:
                resume_then_data_str = u'Не было работы или место работы не указано'
                resume_then_data[resume.id] = resume_then_data_str
        # окончание блока ранее
        
        
        # посчитать все места работы и все время работы
        # список всех дат 
        all_list = []
        all_year = 0
        all_month = 0
        if exp_objs.count() > 0:
            for exp_obj in exp_objs:
                if exp_obj.work_end_date != None:
                    all_list.append([exp_obj.work_end_date, exp_obj.work_start_date])
                else:
                    all_list.append([NOW, exp_obj.work_start_date])

        # переводим в разности 
        if all_list != []:
            all_data_str = ''
            for alst in all_list:
                time_diff = relativedelta(alst[0], alst[1])
                all_year = all_year + time_diff.years
                all_month = all_month + time_diff.months
                
            # перевод месяцев превыщающих 12 в года
            if all_month > 11:  
                all_year = all_year + int(all_month / 12)
                all_month = all_month % 12
            
            # строка
            if all_year == 0 and all_month != 0:
                all_data_str = u'Всего ' + str(exp_objs.count()) + kwplacedict[exp_objs.count()] + u' работы за ' + str(all_month) + kwagedict[math.fabs(all_month)]
            if all_month == 0 and all_year != 0:
                if all_year < 69:
                    all_data_str = u'Всего ' + str(exp_objs.count()) + kwplacedict[exp_objs.count()] + u' работы за ' + str(all_year) + kwagedict[math.fabs(all_year)]
                else:
                    all_data_str = u'Всего ' + str(exp_objs.count()) + kwplacedict[exp_objs.count()] + u' работы за ' + str(all_year) + u'лет'
            if all_month != 0 and all_year != 0:
                if all_year < 69:
                    all_data_str = u'Всего ' + str(exp_objs.count()) + kwplacedict[exp_objs.count()] + u' работы за ' + str(all_year) + ' ' + kwagedict[math.fabs(all_year)] + ' ' + u'и ' + str(all_month) + ' ' + kwmonthdict[math.fabs(all_month)]
                else:
                    all_data_str = u'Всего ' + str(exp_objs.count()) + kwplacedict[exp_objs.count()] + u' работы за ' + str(all_year) + u'лет и' + str(all_month) + kwmonthdict[math.fabs(all_month)]
             
            resume_all_data[resume.id] = all_data_str
        # окончание всех мест работы
        
    
    context['resume_all_data'] = resume_all_data
    context['resume_then_data'] = resume_then_data
    context['resume_now_data'] = resume_now_data
    context['resume_personal_data'] = resume_personal_data
    context['wishes'] = work_wishes
    context['pr_id'] = pr_id
    context['select_resume'] = select_resume
    context['work_page'] = True
    context['resume_search'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    return panel_base_auth(request, context)  
#------------------------------------------------------------------------------------------------------
@render_to('work_resume_view.html')
def work_resume_view(request, resume_id):
    context = {}
    lasting = {}
    no_experience = False
    str_no_work = ''
    sex_dict = {1:u'Мужчина', 2:u'Женщина'}
    month_dict = { 1:u'Январь', 2:u'Февраль' , 3:u'Март',
                   4:u'Апрель', 5:u'Май', 6:u'Июнь',
                   7:u'Июль', 8:u'Август' , 9:u'Сентябрь',
                   10:u'Октябрь', 11:u'Ноябрь', 12:u'Декабрь',
                  }
    # общая инфа по резюме
    resume_obj = HotSpotWorkResumes.objects.get(id=resume_id)
    gender = sex_dict[resume_obj.personal_data.sex]
    NOW = datetime.datetime.now()
    birthday = resume_obj.personal_data.birthday
    rel = relativedelta(NOW, birthday)
    age = rel.years
    if  15 < age < 69:
        age_str = kwagedict[age]
    else:
        age_str = u'лет'
    gender_age = gender + ', ' + str(age) + ' ' + age_str

    # experience
    work_wishes_obj = HotSpotWorkWishes.objects.get(resume__id=resume_id)
    work_exp_objs = HotSpotWorkExperience.objects.filter(work_wishes__id=work_wishes_obj.id).order_by('-work_start_date')
    work_exp_objs_count = HotSpotWorkExperience.objects.filter(work_wishes__id=work_wishes_obj.id).count()
    if work_exp_objs_count != 0:  # по else просто написать, что у соискателя нет опыта работы
        # если сейчас без работы (пишем что сейчас без работы или рабочее место не указано, ниже пишем начало и конец периода)
        if work_exp_objs[0].work_end_date != None:
            no_work_start = work_exp_objs[0].work_end_date  
            no_work_end = datetime.datetime.now()
            let_str = month_dict[no_work_start.month] + ' ' + str(no_work_start.year) + ' - ' + month_dict[no_work_end.month] + ' ' + str(no_work_end.year)
            # продолж. без работы
            rel = relativedelta(no_work_end, no_work_start)
           
            # словарь лет
            if 1 < rel.years < 69:
                years_letters = kwagedict[rel.years]
            else:
                years_letters = u' лет'     
            # строка продолжительность без работы    
            if rel.years == 0 and rel.months != 0:
                dif_str = u'(' + str(rel.months) + ' ' + kwmonthdict[rel.months] + u')'
            if rel.months == 0 and rel.years != 0:
                dif_str = u'(' + str(rel.years) + ' ' + years_letters + u')'           
            if rel.months != 0 and rel.years != 0:
                dif_str = u'(' + str(rel.years) + years_letters + u' и ' + str(rel.months) + kwmonthdict[rel.months] + u')'
            if rel.months == 0 and rel.years == 0:
                str_no_work = u'Сейчас без работы или место работы не указано.' + '<p>' + u'Без работы с этого месяца</p>'
            else:
                str_no_work = u'Сейчас без работы или место работы не указано.' + '<p>' + let_str + dif_str + '</p>'
        # сохраняем все места работы (только разность дат) остальное передадим queryset
        for work_exp_obj in work_exp_objs:
            work_start = work_exp_obj.work_start_date 
            if work_exp_obj.work_end_date == None:
                work_end = datetime.datetime.now()
            else:
                work_end = work_exp_obj.work_end_date
            rel = relativedelta(work_end, work_start)
                
            # словарь лет
            if 0 < rel.years < 69:
                years_letters = kwagedict[rel.years]
            else:
                years_letters = u' лет' 
                   
            # строка разность 
            if rel.years == 0 and rel.months != 0:
                dif_str = u'(' + str(rel.months) + ' ' + kwmonthdict[rel.months] + u')'
            if rel.months == 0 and rel.years != 0:
                dif_str = u'(' + str(rel.years) + ' ' + years_letters + u')'           
            if rel.months != 0 and rel.years != 0:
                dif_str = u'(' + str(rel.years) + years_letters + u' и ' + str(rel.months) + kwmonthdict[math.fabs(rel.months)] + u')'
            if rel.months == 0 and rel.years == 0:
                dif_work = u'(около месяца)'
            else:
                dif_work = dif_str 
            lasting[work_exp_obj.id] = dif_work
    else:
        no_experience = True  # не указано ни одно место работы
    # experience 
    
    # education
    work_ed_and_skills_obj = HotSpotWorkEducationAndSkills.objects.get(resume_id=resume_id)
    work_ed_inst_objs = HotSpotWorkEducationalInstitution.objects.filter(education_and_skills__id=work_ed_and_skills_obj.id).order_by('-graduate_year')
    work_ad_ed_objs = HotSpotWorkAdditionalEducation.objects.filter(education_and_skills__id=work_ed_and_skills_obj.id).order_by('-graduate_year_ad')
    work_langs = HotSpotWorkForeignLanguagesProf.objects.filter(education_and_skills__id=work_ed_and_skills_obj.id)
    work_portfolios = HotSpotWorkPortfolio.objects.filter(education_and_skills__id=work_ed_and_skills_obj.id)
    # education

    context['lasting'] = lasting
    context['str_no_work'] = str_no_work
    context['work_wishes'] = work_wishes_obj
    context['resume'] = resume_obj
    context['gender_age'] = gender_age
    context['work_exp_objs'] = work_exp_objs
    context['no_experience'] = no_experience
    context['work_ed_and_skills_obj'] = work_ed_and_skills_obj
    context['work_ed_inst_objs'] = work_ed_inst_objs
    context['work_ad_ed_objs'] = work_ad_ed_objs
    context['work_langs'] = work_langs
    context['work_portfolios'] = work_portfolios
    context['work_page'] = True
    context['resume_search'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    context['user_name'] = request.user.username
    return context
#=============================================================================================================================
@render_to('work_vacancy_search.html')
def work_vacancy_search(request):
    context = {}
    duties_and_req_objs = []
    pr_id = 0
    

    if request.POST.get("profession_id") != None and request.POST.get("profession_id") != '':
        pr_id = request.POST.get("profession_id")
        prof_obj = HotSpotProfessions.objects.get(id=pr_id)
        duties_and_req_objs = HotSpotWorkDutiesAndRequirements.objects.filter(vacancy_name=prof_obj, vacancy__publication_date__isnull=False).order_by('-vacancy__publication_date')
    else:
        duties_and_req_objs = HotSpotWorkDutiesAndRequirements.objects.filter(vacancy__publication_date__isnull=False).order_by('-vacancy__publication_date')
        
    work_condition_objs = HotSpotWorkConditions.objects.all()
    select_vacancy = HotSpotProfessions.objects.all()
    
    context['duties_and_req_objs'] = duties_and_req_objs
    context['work_condition_objs'] = work_condition_objs
    context['select_vacancy'] = select_vacancy
    context['pr_id'] = pr_id
    context['work_page'] = True
    context['work_vacancy_search'] = True
    work_account_type(request, context)
    context.update(hotspot_identity(request))
    context['user_name'] = request.user.username
    return panel_base_auth(request, context)  # return context original
#============================================================================================================================= 
@render_to('work_vacancy_view.html')
def work_vacancy_view(request, vacancy_id):
    context = {}
    needed_experience = ''
    duties_and_req = HotSpotWorkDutiesAndRequirements.objects.get(vacancy_id=vacancy_id)
    condition = HotSpotWorkConditions.objects.get(duties_and_req=duties_and_req)
    
    if duties_and_req.work_experience != None:
        needed_experience = u'Опыт работы: ' + str(duties_and_req.work_experience) + kwagedict[duties_and_req.work_experience] + u'.'
        
    for_langs = HotSpotWorkForeignLanguagesVacancy.objects.filter(duties_and_req=duties_and_req)
    vacancy_obj = HotSpotWorkVacancies.objects.get(id=vacancy_id)    
     
    context['vacancy_obj'] = vacancy_obj
    context['needed_experience'] = needed_experience
    context['condition'] = condition
    context['duties_and_req'] = duties_and_req
    context['ed_list'] = [1, 2, 4, 6, 3]
    context['for_langs'] = for_langs
    context['work_page'] = True
    context['work_vacancy_search'] = True
    work_account_type(request, context)
    context['user_name'] = request.user.username
    context.update(hotspot_identity(request))
    return context
#=============================================================================================================================
@login_required_job
def work_resume_ajax_publish(request):
    id = request.POST.get('id')
    type = request.POST.get('type')
    # find resume
    resume_obj = HotSpotWorkResumes.objects.get(id=id)
    if type == '1':
        resume_obj.publication_date = datetime.datetime.now()
        resume_obj.save()    
        res_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        # celery task
        # print 'CElERY TASK'
        job_ru_register.delay(request.user.username, resume_obj.id, request.user.email)
        #
    if type == '2':
        resume_obj.publication_date = None
        resume_obj.save()
        res_str = 'None'
    return HttpResponse(res_str)   
#=============================================================================================================================
@login_required_job
def work_vacancy_ajax_publish(request):
    id = request.POST.get('id')
    type = request.POST.get('type')
    # find vacancy
    vacancy_obj = HotSpotWorkVacancies.objects.get(id=id)
    if type == '1':
        vacancy_obj.publication_date = datetime.datetime.now()
        vacancy_obj.save()    
        res_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    if type == '2':
        vacancy_obj.publication_date = None
        vacancy_obj.save()
        res_str = 'None'
    return HttpResponse(res_str)   
#=================================================================================================================================
@login_required_job
def work_vacancy_ajax_delete(request):
    id = request.POST.get('id')
    vacancy_obj = HotSpotWorkVacancies.objects.get(id=int(id))
    vacancy_obj.delete()
    return HttpResponse('res_str')
    
#=================================================================================================================================    
@login_required_job
def work_resume_ajax_delete(request):
    id = request.POST.get('id')
    resume_obj = HotSpotWorkResumes.objects.get(id=int(id))
    resume_obj.delete()
    return HttpResponse('res_str')   
 
#=================================================================================================================================
@render_to('work_need_login.html')
def work_need_login(request):
    context = {}
    context['work_page'] = True
    return panel_base_auth(request, context)

