# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TvForecastSources'
        db.create_table('hot_spot_tv_forecast_sources', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'tvprogramma', ['TvForecastSources'])

        # Adding model 'TvChannels'
        db.create_table('hot_spot_tv_channels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('channel_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('channel_name_eng', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'tvprogramma', ['TvChannels'])

        # Adding model 'TvForecast'
        db.create_table('hot_spot_tv_forecast', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tvprogramma.TvForecastSources'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tvprogramma.TvChannels'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('time_hour', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('time_minute', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True)),
            ('date_get', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'tvprogramma', ['TvForecast'])


    def backwards(self, orm):
        # Deleting model 'TvForecastSources'
        db.delete_table('hot_spot_tv_forecast_sources')

        # Deleting model 'TvChannels'
        db.delete_table('hot_spot_tv_channels')

        # Deleting model 'TvForecast'
        db.delete_table('hot_spot_tv_forecast')


    models = {
        u'tvprogramma.tvchannels': {
            'Meta': {'object_name': 'TvChannels', 'db_table': "'hot_spot_tv_channels'"},
            'channel_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'channel_name_eng': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tvprogramma.tvforecast': {
            'Meta': {'object_name': 'TvForecast', 'db_table': "'hot_spot_tv_forecast'"},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tvprogramma.TvChannels']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'date_get': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tvprogramma.TvForecastSources']"}),
            'time_hour': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'time_minute': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'tvprogramma.tvforecastsources': {
            'Meta': {'object_name': 'TvForecastSources', 'db_table': "'hot_spot_tv_forecast_sources'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tvprogramma']