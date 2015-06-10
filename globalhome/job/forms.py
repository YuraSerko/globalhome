# coding: utf-8
from django import forms
from job import models
from django.conf import settings
from job.models import HotSpotWorkJobSeekerPersonalData
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime, timedelta
from django.utils.translation import ugettext_lazy as _  
from job.models import HotSpotCompetitorCity
from billing.models import BillserviceAccount
from job.models import HotSpotWorkExperience
from lib.widgets import MonthYearWidget
from job.models import HotSpotCompetitorCity
from job.models import HotSpotWorkEducationAndSkills
from job.models import HotSpotWorkEducationalInstitution
from job.models import HotSpotWorkForeignLanguagesProf
from job.models import HotSpotWorkAdditionalEducation  
from job.models import HotSpotWorkPortfolio
from job.models import HotSpotWorkWishes
from job.models import WORK_MODE_CHOICES
from job.models import HotSpotWorkEmployerData
from job.models import HotSpotWorkDutiesAndRequirements
from job.models import HotSpotWorkForeignLanguagesVacancy
from job.models import HotSpotWorkConditions
from account.forms import UserRegistrationForm
from job.models import HotSpotWorkForeignLanguagesList 


class HotSpotWorkJobSeekerPersonalDataForm(forms.ModelForm):
    class Meta:
        model = HotSpotWorkJobSeekerPersonalData
        fields = ['photo', 'last_name', 'first_name',
                   'second_name', 'sex', 'birthday',
                   'citizenship', 'living_city', 'metro_station',
                   'adress', 'main_tel_code', 'main_tel_number',
                   'additional_tel_number', 'additional_tel_code', ]
        widgets = {
        'birthday': SelectDateWidget(years=range(1900, \
                                     datetime.now().year),
                                     attrs={"style" : "width: 95px;"}),
      
        }
   
    def __init__(self, *args, **kwargs):
        super(HotSpotWorkJobSeekerPersonalDataForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if f == 'sex':
                if not bool(self.fields[f].choices[0][0]):
                    self.fields[f].choices = [('', _(u'Not defined'))] + self.fields[f].choices[1:]
    
 
    def clean(self):
        cleaned_data = self.cleaned_data
        print 'in method clean'
        fn = cleaned_data.get('first_name')
        # is None
        if fn == None:
            raise forms.ValidationError("check first_name")
        sn = cleaned_data.get('second_name')
        if sn == None:
            raise forms.ValidationError("check second_name")
        sx = cleaned_data.get('sex')
        if sx == None:
            raise forms.ValidationError("check sex")
        b_day = cleaned_data.get('birthday')
        if b_day == None:
            raise forms.ValidationError("check birthday")
        cship = cleaned_data.get('citizenship')
        if cship == None:
            raise forms.ValidationError("check citizenship")
        lcity = cleaned_data.get('living_city')
        if lcity == None:
            raise forms.ValidationError("check living_city")
        tel_code = cleaned_data.get('main_tel_code')
        if tel_code == None:
            raise forms.ValidationError("check main_tel_code")
        tel_number = cleaned_data.get('main_tel_number')
        if tel_number == None:
            raise forms.ValidationError("check tel_number")
        ad_tel_code = self.data['additional_tel_code']
        ad_tel_number = self.data['additional_tel_number']
        import re
        reg_ex1 = re.match("[0-9]+", ad_tel_code)
        if (reg_ex1 == None and ad_tel_code != '') :
            raise forms.ValidationError("only numbers")
        reg_ex2 = re.match("[0-9]+", ad_tel_number)
        if reg_ex2 == None and ad_tel_number != '':
            raise forms.ValidationError("only numbers")
        
        picture = self.cleaned_data.get('photo')
        if picture is None:
            raise forms.ValidationError(u'Not image filetype')
           
        
        if picture != 'uploads/work_photo/None/no-img.jpg':        
            try:
                if len(picture) > (2000 * 1024):
                    raise forms.ValidationError(u'File size may not exceed 2000k.')
            except AttributeError:
                pass
        
        return cleaned_data
    
    

#==============================================================================================================
class HotSpotWorkExperienceForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkExperience
        
        fields = [ 'work_start_date', 'work_end_date',
                  'city', 'org_name', 'org_site', 'branch_activity',
                  'position', 'taken_position_level', 'duties_achievements', 'deleted', 'till_now' ]
        widgets = {
        'work_start_date': MonthYearWidget(years=range(1920, \
                                     datetime.now().year + 1),
                                     attrs={"style" : "width: 82px;"}),
                    
        'work_end_date': MonthYearWidget(years=range(1920, \
                                     datetime.now().year + 1),
                                     attrs={"style" : "width: 82px;"}),
        'duties_achievements':forms.Textarea(attrs={'cols':46, 'rows':4, 'style':"resize:vertical;"}),
        'till_now':forms.CheckboxInput(attrs={'onchange':'fun_till_now(this)'}),
        }
      
    
#====================================================================================================================
class HotSpotWorkEducationAndSkillsForm(forms.ModelForm):
    class Meta:
        model = HotSpotWorkEducationAndSkills
        fields = ['education_level', 'professional_skills', 'driving_license_A',
                  'driving_license_B', 'driving_license_C', 'driving_license_D',
                  'driving_license_E', 'has_car', 'has_medical_book', ]
        widgets = {
        'professional_skills':forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:vertical;"}),
               
        }
#====================================================================================================================
class HotSpotWorkEducationalInstitutionForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkEducationalInstitution
        fields = [ 'institution_name', 'faculty_specialty', 'graduate_year', 'deleted']
 
#====================================================================================================================
class HotSpotWorkForeignLanguagesProfForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkForeignLanguagesProf
        fields = [ 'language', 'proficiency_language_level']
#====================================================================================================================
class HotSpotWorkAdditionalEducationForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkAdditionalEducation
        fields = [ 'institution_name', 'course_name', 'graduate_year_ad']
#====================================================================================================================
class HotSpotWorkPortfolioForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkPortfolio
        fields = [ 'portfolio_link']
#====================================================================================================================
class HotSpotWorkWishesForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    no_exp = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkWishes
        fields = [ 'desirable_position', 'salary', 'salary_um', 'additional_name',
                  'work_mode', 'employment_type', 'work_type', 'business_trip',
                  'specialization', 'living_city' ]
       
        widgets = {
        'work_mode':forms.RadioSelect(attrs={"choices": "WORK_MODE_CHOICES", "initial":'1'}),
        'employment_type':forms.RadioSelect(),
        'work_type':forms.RadioSelect(),
        'business_trip':forms.RadioSelect(),
        }

#====================================================================================================================

class HotSpotWorkEmployerDataForm(forms.ModelForm):
    class Meta:
        model = HotSpotWorkEmployerData
        fields = [ 'city', 'company_name', 'ownership_form', 'ownership_not_to_competitor',
                  'employer_type', 'activity', 'INN', 'telephone_code',
                  'telephone_number', 'staff', 'site_url', 'company_info', 'name',
                  'surname', 'contact_code', 'contact_phone_number', 'contact_phone_additional',
                  'telephone_code_add', 'telephone_number_add', ]
       
        widgets = {      
        'employer_type':forms.RadioSelect(),
        'company_info':forms.Textarea(attrs={'cols':65, 'rows':6, 'style':"resize:vertical;"}),
        }

#====================================================================================================================
class HotSpotWorkDutiesAndRequirementsForm(forms.ModelForm):
    class Meta:
        model = HotSpotWorkDutiesAndRequirements
        fields = [  'vacancy_name', 'vacancy_additional_name', 'taken_position_level',
                  'activity', 'vacancy_discription', 'work_experience', 'education_level',
                  'age_from', 'age_to', 'sex', 'nationality', 'work_permission',
                  'medical_book', 'international_passport', 'driving_license_A', 'driving_license_B',
                  'driving_license_C', 'driving_license_D', 'driving_license_E',
                  'car_needed', 'additional_requirements', 'no_exp_strict',
                  ]
       
        widgets = {
        'vacancy_discription':forms.Textarea(attrs={'cols':60, 'rows':6, 'style':"resize:vertical;"}),
        'additional_requirements':forms.Textarea(attrs={'cols':60, 'rows':6, 'style':"resize:vertical;"}),
        'sex':forms.RadioSelect(),
        }
#====================================================================================================================
class HotSpotWorkForeignLanguagesVacancyForm(forms.ModelForm):
    deleted = forms.BooleanField(required=False)
    class Meta:
        model = HotSpotWorkForeignLanguagesVacancy
        fields = [ 'language', 'language_level']
#====================================================================================================================
class HotSpotWorkConditionsForm(forms.ModelForm):
    class Meta:
        model = HotSpotWorkConditions
        fields = [ 'salary_from', 'salary_to',
                  'bonus', 'city', 'transporting_help', 'address',
                  'region', 'work_mode', 'employment_type',
                  'work_type', 'open_air', 'traveling',
                  'business_trip', 'registration', 'DMS_employee',
                  'DMS_employee_family', 'mobile',
                  'food', 'transport', 'special_clothes',
                  'offical_car', 'sport_hall', 'corporate_training',
                  'career_growth', 'additionl_cond',
                  ]
        widgets = {
        'work_mode':forms.RadioSelect(),
        'employment_type':forms.RadioSelect(),
        'work_type':forms.RadioSelect(),
        'additionl_cond':forms.Textarea(attrs={'cols':45, 'rows':6, 'style':"resize:vertical;"}),
        }
#====================================================================================================================    
