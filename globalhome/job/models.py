# coding: utf-8
from django.db import models
from billing.models import BillserviceAccount
import datetime

# Create your models here.
#====================================================================================================
class HotSpotWorkTimeZone(models.Model):
    id = models.AutoField(primary_key=True)
    designation = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100)
    class Meta:
        db_table = 'hot_spot_work_time_zone'


#=====================================================================================================
class HotSpotCompetitorRegion(models.Model):
    id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=300)
    jobru_region_id = models.CharField(max_length=10)
    class Meta:
        db_table = 'hot_spot_competitor_region'
    def __unicode__(self):
        return '%s' % (self.region_name) 
    
#======================================================================================================
# модель для хранения города проживания соискателя/работодателя
class HotSpotCompetitorCity(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.ForeignKey(HotSpotCompetitorRegion, default=0)
    city = models.CharField(max_length=300)   
    has_metro = models.BooleanField(default=False)
    jobru_city_id = models.CharField(max_length=10, default=0) 
    city_full_name = models.CharField(max_length=255)
    class Meta:
        db_table = 'hot_spot_competitor_city'
    def __unicode__(self):
        return '%s' % (self.city_full_name)
#         return  u'%s (%s)' % (self.city, self.region.region_name)
#======================================================================================================
# модель для хранения линий метро городов России
class HotSpotMetroLines(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.ForeignKey(HotSpotCompetitorCity)
    line = models.CharField(max_length=300)
     
    class Meta:
        db_table = 'hot_spot_metro_lines'
#======================================================================================================
# модель для хранения станций метро городов России
class HotSpotMetroStations(models.Model):
    id = models.AutoField(primary_key=True)
    line = models.ForeignKey(HotSpotMetroLines)
    station = models.CharField(max_length=300)
     
    class Meta:
        db_table = 'hot_spot_metro_stations'
    def __unicode__(self):
        return  u'%s(%s)' % (self.station, self.line.line)
#======================================================================================================
# сферы деятельности 
class HotSpotActivityFields(models.Model):
    id = models.AutoField(primary_key=True)
    activity_field = models.CharField(max_length=300)
    job_ru_activity_id = models.IntegerField()
      
    class Meta:
        db_table = 'hot_spot_work_activity_fields'
    def __unicode__(self):
        return  u'%s' % (self.activity_field)
#======================================================================================================
# специализации
class HotSpotSpecializations(models.Model):
    id = models.AutoField(primary_key=True)
    activity_field = models.ForeignKey(HotSpotActivityFields)
    specialization = models.CharField(max_length=300)
    job_ru_spec_id = models.IntegerField()
    class Meta:
        db_table = 'hot_spot_work_specializations'     
#======================================================================================================
# группы профессий
class HotSpotProfessionGroup(models.Model):
    id = models.AutoField(primary_key=True)
    profession_group = models.CharField(max_length=300)
     
    class Meta:
        db_table = 'hot_spot_work_profession_group'
#======================================================================================================
# профессии
class HotSpotProfessions(models.Model):
    id = models.AutoField(primary_key=True)
    profession_group = models.ForeignKey(HotSpotProfessionGroup)
    profession = models.CharField(max_length=300)
     
    class Meta:
        db_table = 'hot_spot_work_professions'
    def __unicode__(self):
        return  u'%s' % (self.profession)



class HotSpotWorkNationality(models.Model):
    id = models.AutoField(primary_key=True)
    nationality = models.CharField(max_length=100)
    jobru_nat_id = models.IntegerField()
    class Meta:
        db_table = 'hot_spot_work_nationalities'
    def __unicode__(self):
        return  u'%s' % (self.nationality)

        
# from account.models import SEX_CHOICES
from django.utils.translation import ugettext_lazy as _ 
SEX_CHOICES = [(1, _(u"M")), (2, _(u"F"))]
CITIZENSHIP_CHOICES = [ (1, _(u"Россия")), (2, _(u"Беларусь")), (3, _(u"Украина")), (4, _(u"Казахстан")), (5, _(u"Узбекистан"))]
  
# личные данные пользователя раздела работа
class HotSpotWorkJobSeekerPersonalData(models.Model):
    id = models.AutoField(primary_key=True)
    billservac = models.ForeignKey(BillserviceAccount)
    first_name = models.CharField(verbose_name=_(u"First name"), max_length=255)
    second_name = models.CharField(verbose_name=_(u"Second name"), max_length=255)
    last_name = models.CharField(verbose_name=_(u"Last name"), max_length=255, null=True, blank=True)
    sex = models.IntegerField(verbose_name=_(u"Sex"), choices=SEX_CHOICES)
    birthday = models.DateField(verbose_name=_(u"Birsday"), null=True)
    citizenship = models.ForeignKey(HotSpotWorkNationality)
    living_city = models.ForeignKey(HotSpotCompetitorCity)
    metro_station = models.ForeignKey(HotSpotMetroStations, null=True, blank=True)
    adress = models.CharField(max_length=300, null=True, blank=True)
    main_tel_code = models.IntegerField()
    main_tel_number = models.IntegerField()
    additional_tel_code = models.IntegerField(null=True, blank=True)
    additional_tel_number = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to='uploads/work_photo', default='uploads/work_photo/None/no-img.jpg')
    time_zone = models.ForeignKey(HotSpotWorkTimeZone, null=True, blank=True)
           
    class Meta:
        db_table = 'hot_spot_work_job_seeker_personal_data'

     
     
         
       
         
class HotSpotWorkResumes(models.Model):
    id = models.AutoField(primary_key=True)
    personal_data = models.ForeignKey(HotSpotWorkJobSeekerPersonalData)
    create_date = models.DateTimeField(default=datetime.datetime.now())
    publication_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_resumes'
  






SALARY_UM_CHOICES = [ (1, _(u"руб./мес.")), (2, _(u"$/мес.")), (3, _(u"€/мес."))]
WORK_MODE_CHOICES = [ (1, _(u"полный день")), (2, _(u"свободный / гибкий график")), (3, _(u"сменный график")), (4, _(u"любой график"))]
EMPLOYMENT_TYPE_CHOICES = [ (1, _(u"постоянная работа")), (2, _(u"временная или проектная работа")), (3, _(u"стажировка")), (4, _(u"волонтерство"))]
BUSINESS_TRIP_CHOICES = [ (0, _(u"Невозможны")), (1, _(u"Возможны"))]
WORK_TYPE_CHOICES = [ (1, _(u"на территории работодателя ")), (2, _(u"на дому / удаленная"))] 
   
class HotSpotWorkWishes(models.Model):
    resume = models.ForeignKey(HotSpotWorkResumes)    
    desirable_position = models.ForeignKey(HotSpotProfessions, related_name='wishes_position',)
    salary = models.IntegerField(null=True, blank=True)
    salary_um = models.IntegerField(choices=SALARY_UM_CHOICES, default=0)
    additional_name = models.ManyToManyField(HotSpotProfessions, null=True, blank=True, related_name='wishes_additional_position',)
    work_mode = models.IntegerField(default=1, choices=WORK_MODE_CHOICES)  # режим работы
    employment_type = models.IntegerField(choices=EMPLOYMENT_TYPE_CHOICES, default=1)  # тип занятости
    work_type = models.IntegerField(choices=WORK_TYPE_CHOICES, default=1)  # тип работы
    business_trip = models.IntegerField(choices=BUSINESS_TRIP_CHOICES, default=0)
    specialization = models.ManyToManyField(HotSpotSpecializations)
    living_city = models.ManyToManyField(HotSpotCompetitorCity)
    # no_exp = models.BooleanField(default=False, blank=True,)         
    class Meta:
        db_table = 'hot_spot_work_wishes'










  
TAKEN_POSITION_LEVEL_CHOICES = [ (1, _(u"Стажер, начало кареьры")), (2, _(u"Рабочий, служащий")),
                                 (3, _(u"Квалифицированный специалист")), (4, _(u"Руководитель среднего звена")),
                                 (5, _(u"Топ-менеджмент")), (6, _(u"Собственник, владелец бизнеса")), ]
class HotSpotWorkExperience(models.Model):
    # id = models.AutoField(primary_key=True)
    # resume = models.ForeignKey(HotSpotWorkResumes)    
    work_start_date = models.DateField()    
    work_end_date = models.DateField(null=True, blank=True)
    till_now = models.BooleanField(default=False, blank=True,)
    city = models.ForeignKey(HotSpotCompetitorCity)
    org_name = models.CharField(max_length=300)
    org_site = models.CharField(max_length=300, null=True, blank=True)
    branch_activity = models.ForeignKey(HotSpotActivityFields)
    position = models.ForeignKey(HotSpotProfessions)
    taken_position_level = models.IntegerField(choices=TAKEN_POSITION_LEVEL_CHOICES)
    duties_achievements = models.CharField(max_length=2000)
    work_wishes = models.ForeignKey(HotSpotWorkWishes)
    class Meta:
        db_table = 'hot_spot_work_experience'
        unique_together = ("work_start_date", "org_name", "position",)
           
          
          
         

    
  
  
   
EDUCATION_LEVEL_CHOICES = [ (1, _(u"Неполное среднее")), (2, _(u"Среднее")),
                                 (3, _(u"Среднее специальное")), (4, _(u"Неоконч. высшее")),
                                 (5, _(u"Студент")), (6, _(u"Высшее")),
                                 (7, _(u"МВА")), (8, _(u"Ученая степень")), ]
class HotSpotWorkEducationAndSkills(models.Model):
    id = models.AutoField(primary_key=True)
    resume = models.ForeignKey(HotSpotWorkResumes)
    education_level = models.IntegerField(choices=EDUCATION_LEVEL_CHOICES) 
    professional_skills = models.CharField(max_length=2000, blank=True, null=True)
    driving_license_A = models.BooleanField(default=False, blank=True,)
    driving_license_B = models.BooleanField(default=False, blank=True,)
    driving_license_C = models.BooleanField(default=False, blank=True,)
    driving_license_D = models.BooleanField(default=False, blank=True,)
    driving_license_E = models.BooleanField(default=False, blank=True,)
    has_car = models.BooleanField(default=False, blank=True,)
    has_medical_book = models.BooleanField(default=False, blank=True,)
    class Meta:
        db_table = 'hot_spot_work_educational_and_skills'



YEAR_CHOICES = []
for y in range(1930, 2020):
    z = ()
    z = (y, y)
    YEAR_CHOICES.append(z)
class HotSpotWorkEducationalInstitution(models.Model):
    id = models.AutoField(primary_key=True)
    education_and_skills = models.ForeignKey(HotSpotWorkEducationAndSkills)
    institution_name = models.CharField(max_length=100)
    faculty_specialty = models.CharField(max_length=100)
    graduate_year = models.IntegerField(choices=YEAR_CHOICES)
    class Meta:
        db_table = 'hot_spot_work_education_institution'
        unique_together = ("institution_name", "faculty_specialty", "graduate_year",)
   
class HotSpotWorkForeignLanguagesList(models.Model):
    id = models.AutoField(primary_key=True)
    language = models.CharField(max_length=100)
    job_ru_lan_id = models.IntegerField()
    class Meta:
        db_table = 'hot_spot_work_foreign_languages_list'
    def __unicode__(self):
        return  u'%s' % (self.language)
   
PROFICIENCY_LANGUAGE_LEVEL = [ (1, _(u"начальный")), (2, _(u"средний, профессиональная терминология")), (3, _(u"свободный")) ]     
class HotSpotWorkForeignLanguagesProf(models.Model):
    id = models.AutoField(primary_key=True)
    education_and_skills = models.ForeignKey(HotSpotWorkEducationAndSkills)
    language = models.ForeignKey(HotSpotWorkForeignLanguagesList, blank=True, null=True)
    proficiency_language_level = models.IntegerField(choices=PROFICIENCY_LANGUAGE_LEVEL, blank=True, null=True, default=0)
    unique_together = ("language", "proficiency_language_level")
    class Meta:
        db_table = 'hot_spot_work_foreign_languages_prof'
              
      
class HotSpotWorkAdditionalEducation(models.Model):
    id = models.AutoField(primary_key=True)
    education_and_skills = models.ForeignKey(HotSpotWorkEducationAndSkills)
    institution_name = models.CharField(max_length=100, blank=True, null=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)
    graduate_year_ad = models.IntegerField(choices=YEAR_CHOICES, blank=True, null=True)
    class Meta:
        db_table = 'hot_spot_work_additional_education'
              
class HotSpotWorkPortfolio(models.Model):
    id = models.AutoField(primary_key=True)
    education_and_skills = models.ForeignKey(HotSpotWorkEducationAndSkills)
    portfolio_link = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        db_table = 'hot_spot_work_portfolio'
         
         
#        
OWNERSHIP_FORM_CHOICES = [ (1, _(u"OOO")), (2, _(u"ОАО")), (4, _(u"ЗАО")),
                           (5, _(u"УП")), (6, _(u"ТОО")), (7, _(u"Некоммерческая организация")),
                           (8, _(u"Общественная организация")), (9, _(u"Фонд")), (10, _(u"Государственная корпорация")),
                           (11, _(u"ИП")), (12, _(u"Дргое")) ]
DIRECT_EMPLOYER_CHOICES = [ (1, _(u"Прямой работадатель")), (2, _(u"Кадровое агентство"))]
STAFF_CHOICES = [ (1, _(u"до 50 человек")), (2, _(u"от 50 до 300чел")),
                  (3, _(u"от 300 до 1000чел.")), (4, _(u"больше 1000 чел.")), (5, _(u"более 10000 чел.")) ]  
class HotSpotWorkEmployerData(models.Model):
    id = models.AutoField(primary_key=True)
    billservac = models.ForeignKey(BillserviceAccount)
    city = models.ForeignKey(HotSpotCompetitorCity)
    company_name = models.CharField(max_length=100)
    ownership_form = models.IntegerField(choices=OWNERSHIP_FORM_CHOICES)
    ownership_not_to_competitor = models.BooleanField(default=False)
    employer_type = models.IntegerField(choices=DIRECT_EMPLOYER_CHOICES, default=1)
    activity = models.ForeignKey(HotSpotActivityFields)
    INN = models.IntegerField(blank=True, null=True)
    telephone_code = models.IntegerField()
    telephone_number = models.IntegerField()
    telephone_code_add = models.IntegerField(blank=True, null=True)
    telephone_number_add = models.IntegerField(blank=True, null=True)
    staff = models.IntegerField(choices=STAFF_CHOICES)
    site_url = models.CharField(max_length=100, blank=True, null=True)
    company_info = models.CharField(max_length=1000)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    contact_code = models.IntegerField(null=True, blank=True)
    contact_phone_number = models.IntegerField(null=True, blank=True)
    contact_phone_additional = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_employer_data'
        
     
#=============================================================================================  

  
class HotSpotWorkVacancies(models.Model):
    id = models.AutoField(primary_key=True)
    employer_data = models.ForeignKey(HotSpotWorkEmployerData)
    create_date = models.DateTimeField(default=datetime.datetime.now())
    publication_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_vacancies'    
    
#=============================================================================================================
#=============================================================================================================

    

 
VACANCY_SEX_CHOICES = [ (1, _(u"не важно")), (2, _(u"мужской")), (3, _(u"женский")) ]  
  
class HotSpotWorkDutiesAndRequirements(models.Model):
    id = models.AutoField(primary_key=True)
    vacancy = models.ForeignKey(HotSpotWorkVacancies)
    vacancy_name = models.ForeignKey(HotSpotProfessions, related_name='vacancy')
    vacancy_additional_name = models.ManyToManyField(HotSpotProfessions, null=True, blank=True, related_name='vacancy_additional')
    taken_position_level = models.IntegerField(choices=TAKEN_POSITION_LEVEL_CHOICES)
    activity = models.ManyToManyField(HotSpotSpecializations)
    vacancy_discription = models.CharField(max_length=1000)
    work_experience = models.IntegerField(null=True, blank=True)
    no_exp_strict = models.BooleanField(default=False)
    education_level = models.IntegerField(choices=EDUCATION_LEVEL_CHOICES, null=True, blank=True) 
    age_from = models.IntegerField(null=True, blank=True)
    age_to = models.IntegerField(null=True, blank=True)
    sex = models.IntegerField(choices=VACANCY_SEX_CHOICES, default=1)
    nationality = models.ManyToManyField(HotSpotWorkNationality, null=True, blank=True)
    work_permission = models.BooleanField(default=False)
    medical_book = models.BooleanField(default=False)
    international_passport = models.BooleanField(default=False)
    driving_license_A = models.BooleanField(default=False)
    driving_license_B = models.BooleanField(default=False)
    driving_license_C = models.BooleanField(default=False)
    driving_license_D = models.BooleanField(default=False)
    driving_license_E = models.BooleanField(default=False)
    car_needed = models.BooleanField(default=False)
    additional_requirements = models.CharField(max_length=1000, null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_duties_and_requirements'
      
#=======================================================================================================
class HotSpotWorkForeignLanguagesVacancy(models.Model):
    id = models.AutoField(primary_key=True)
    duties_and_req = models.ForeignKey(HotSpotWorkDutiesAndRequirements)
    language = models.ForeignKey(HotSpotWorkForeignLanguagesList, blank=True, null=True)
    language_level = models.IntegerField(choices=PROFICIENCY_LANGUAGE_LEVEL, null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_foreign_languages_vacancy'
        unique_together = ("duties_and_req", "language", "language_level",)

#==============================================================================================================
    
class HotSpotWorkConditions(models.Model):
    id = models.AutoField(primary_key=True)
    duties_and_req = models.ForeignKey(HotSpotWorkDutiesAndRequirements)
    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)
    bonus = models.BooleanField(default=False)
    city = models.ForeignKey(HotSpotCompetitorCity, related_name='condition_city')
    transporting_help = models.BooleanField(default=False)
    address = models.CharField(max_length=100, null=True, blank=True)
    region = models.ForeignKey(HotSpotCompetitorCity, related_name='condition_region', null=True, blank=True)
    work_mode = models.IntegerField(default=1, choices=WORK_MODE_CHOICES)
    employment_type = models.IntegerField(choices=EMPLOYMENT_TYPE_CHOICES, default=1)
    work_type = models.IntegerField(choices=WORK_TYPE_CHOICES, default=1)
    open_air = models.BooleanField(default=False)
    traveling = models.BooleanField(default=False)
    business_trip = models.BooleanField(default=False)
    registration = models.BooleanField(default=False)
    DMS_employee = models.BooleanField(default=False)
    DMS_employee_family = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    transport = models.BooleanField(default=False)
    special_clothes = models.BooleanField(default=False)
    offical_car = models.BooleanField(default=False)
    sport_hall = models.BooleanField(default=False)
    corporate_training = models.BooleanField(default=False)
    career_growth = models.BooleanField(default=False)
    additionl_cond = models.CharField(max_length=1000, null=True, blank=True)
    class Meta:
        db_table = 'hot_spot_work_conditions'
    
#==============================================================================================================    
JOBRUCREATEDTYPES = [  (1, _(u'резюме')), (2, _(u'вакансия'))  ]
class HotSpotWorkJobRuCreated(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    mobi_mail = models.CharField(max_length=255)
    mobi_mail_pas = models.CharField(max_length=255)
    type = models.IntegerField(choices=JOBRUCREATEDTYPES)
    doc_id = models.IntegerField()
    get_param = models.CharField(max_length=100)
    class Meta:
        db_table = 'hot_spot_work_jobru_created'   
