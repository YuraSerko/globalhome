from django.db import models

# Create your models here.

class TvChannels(models.Model):
    id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=300)
    channel_image  = models.ImageField(upload_to='media/img/channels', null=True)
    channel_name_eng = models.CharField(max_length = 300)
    class Meta:
        db_table = 'hot_spot_tv_channels'
#=============================================================================================================================    
class TvForecastSources(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)    
    class Meta:
        db_table = 'hot_spot_tv_forecast_sources'      
#============================================================================================================================ 
class TvForecast(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(TvForecastSources)
    channel = models.ForeignKey(TvChannels)
    date = models.DateTimeField()
    time_hour = models.IntegerField(null=True)
    time_minute = models.IntegerField(null=True)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, null=True)
    date_get = models.DateTimeField()
    #session = models.IntegerField(null=True)
    class Meta:
        db_table = 'hot_spot_tv_forecast'
       
