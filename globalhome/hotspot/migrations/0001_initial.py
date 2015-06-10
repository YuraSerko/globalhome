# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IPPool'
        db.create_table(u'hotspot_ippool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('start_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('end_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('next_ippool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.IPPool'], null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['IPPool'])

        # Adding model 'IPInUse'
        db.create_table(u'hotspot_ipinuse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.IPPool'])),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('disabled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dynamic', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hotspot', ['IPInUse'])

        # Adding model 'Games_Section'
        db.create_table(u'hotspot_games_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'hotspot', ['Games_Section'])

        # Adding model 'Games'
        db.create_table(u'hotspot_games', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('banner', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('section', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('section2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('img', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('http', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'hotspot', ['Games'])

        # Adding M2M table for field section_game on 'Games'
        m2m_table_name = db.shorten_name(u'hotspot_games_section_game')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('games', models.ForeignKey(orm[u'hotspot.games'], null=False)),
            ('games_section', models.ForeignKey(orm[u'hotspot.games_section'], null=False))
        ))
        db.create_unique(m2m_table_name, ['games_id', 'games_section_id'])

        # Adding model 'Nas'
        db.create_table('nas_nas', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='mikrotik3', max_length=32)),
            ('identify', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('ipaddress', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('login', self.gf('django.db.models.fields.CharField')(default='admin', max_length=255, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('allow_pptp', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_pppoe', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_ipn', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user_add_action', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user_enable_action', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user_disable_action', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user_delete_action', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('vpn_speed_action', self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True)),
            ('ipn_speed_action', self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True)),
            ('reset_action', self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True)),
            ('confstring', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('subacc_disable_action', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('subacc_enable_action', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('subacc_add_action', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('subacc_delete_action', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('subacc_ipn_speed_action', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('snmp_version', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('speed_vendor_1', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('speed_vendor_2', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('speed_attr_id1', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('speed_attr_id2', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('speed_value1', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('speed_value2', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('acct_interim_interval', self.gf('django.db.models.fields.IntegerField')(default=60, null=True, blank=True)),
            ('data_centr_tarif', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_centr.Tariff'], null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['Nas'])

        # Adding model 'Prefecturs'
        db.create_table('prefecturs', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=512)),
            ('adress', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('tel_numbers', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('subway_station', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('web_site', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('x', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('y', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('add_information', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['Prefecturs'])

        # Adding model 'DistrictAdministration'
        db.create_table('district_administration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefecturs', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.Prefecturs'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('adress', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('tel_numbers', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('subway_station', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('web_site', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('x', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('y', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('add_information', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['DistrictAdministration'])

        # Adding model 'HomeAdministration'
        db.create_table('home_administration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('district_administration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.DistrictAdministration'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('adress', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('tel_numbers', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('subway_station', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('web_site', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('x', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('y', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('add_information', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['HomeAdministration'])

        # Adding model 'HotSpotRate'
        db.create_table('hot_spot_rate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('char_code', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('nominal', self.gf('django.db.models.fields.IntegerField')(max_length=512)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal(u'hotspot', ['HotSpotRate'])

        # Adding model 'HotSpotWeatger'
        db.create_table('hot_spot_weather', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('temp_now', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('temp_d_n', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('spr_class', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal(u'hotspot', ['HotSpotWeatger'])

        # Adding model 'HotSpotQueryStatistic'
        db.create_table('hot_spot_query_statistic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query_string', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['HotSpotQueryStatistic'])

        # Adding model 'HotSpotReview'
        db.create_table('hot_spot_review', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact_face', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('adres', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('mail', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('telnumber', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('was_treated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['HotSpotReview'])

        # Adding model 'MainNews'
        db.create_table('hot_spot_main_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title_news', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('discription_news', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('link_news', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('img_news', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('portal_name', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('portal_link', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('portal_diskription', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('portal_copyright', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('date_get_news', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('news_type', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('img_news_root', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['MainNews'])

        # Adding model 'WeatherCountries'
        db.create_table('hot_spot_weather_countries', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_rus_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city_rus_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country_eng_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city_eng_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('yandex_city_id', self.gf('django.db.models.fields.IntegerField')()),
            ('openweathermap_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('region_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'hotspot', ['WeatherCountries'])

        # Adding model 'MobiWeather'
        db.create_table('hot_spot_mobi_weather', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('taking_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_date_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cloud', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('temp_from', self.gf('django.db.models.fields.FloatField')()),
            ('temp_to', self.gf('django.db.models.fields.FloatField')()),
            ('wind_speed', self.gf('django.db.models.fields.FloatField')()),
            ('wind_dir', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('pressure', self.gf('django.db.models.fields.FloatField')()),
            ('humidity', self.gf('django.db.models.fields.FloatField')()),
            ('city_weather_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.WeatherCountries'], null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['MobiWeather'])

        # Adding model 'MobiOrganizationsUnique'
        db.create_table('hot_spot_mobi_organizations_unique', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('org_type', self.gf('django.db.models.fields.IntegerField')()),
            ('yan_id', self.gf('django.db.models.fields.IntegerField')()),
            ('org_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('hours', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('x', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=16, decimal_places=10, blank=True)),
            ('y', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=16, decimal_places=10, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('equal_coord_range', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hotspot', ['MobiOrganizationsUnique'])

        # Adding model 'MobiOrganizationsUserChanges'
        db.create_table('hot_spot_mobi_organization_user_changes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('org_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.MobiOrganizationsUnique'])),
            ('u_org_name', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('u_address', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('u_url', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('u_phone', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('u_hours', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('user_email', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('applied', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('to_del', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hotspot', ['MobiOrganizationsUserChanges'])

        # Adding model 'VideoGenre'
        db.create_table('hot_spot_video_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translit_genre', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'hotspot', ['VideoGenre'])

        # Adding model 'Video_Rate'
        db.create_table('rate_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rating_votes', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('rating_score', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'hotspot', ['Video_Rate'])

        # Adding model 'Comments_Of_Video'
        db.create_table('hotspot_video_comments', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('commentator_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('comment_content', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('add_to_site', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hotspot', ['Comments_Of_Video'])

        # Adding model 'HotSpot_Bad_Video_Link'
        db.create_table('hot_spot_bad_video_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact_face', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('mail', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('broken_video_id', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['HotSpot_Bad_Video_Link'])

        # Adding model 'Video'
        db.create_table('hot_spot_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.IntegerField')()),
            ('internal_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('orig_title', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('video_type', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('genres_client_view', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=6000, blank=True)),
            ('time', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('imdb_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('rating_by', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('image_link', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('player_video_url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=9200)),
            ('premiere_date', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('age_restrictions', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('quality', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('sound', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('budget', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('director', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cast', self.gf('django.db.models.fields.CharField')(max_length=600, blank=True)),
            ('screenplay', self.gf('django.db.models.fields.CharField')(max_length=600, blank=True)),
            ('kp_rating', self.gf('django.db.models.fields.CharField')(max_length=600, null=True, blank=True)),
            ('imdb_rating', self.gf('django.db.models.fields.CharField')(max_length=600, null=True, blank=True)),
            ('label_text', self.gf('django.db.models.fields.CharField')(default=1, max_length=50000, blank=True)),
            ('one_serial_links', self.gf('django.db.models.fields.CharField')(default=1, max_length=50000, blank=True)),
            ('date_aded', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('translit_video_name', self.gf('django.db.models.fields.CharField')(max_length=400, unique=True, null=True, blank=True)),
            ('site_rating', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.Video_Rate'], null=True, blank=True)),
            ('id_gid_film', self.gf('django.db.models.fields.CharField')(max_length=1000, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'hotspot', ['Video'])

        # Adding M2M table for field genres on 'Video'
        m2m_table_name = db.shorten_name('hot_spot_video_genres')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('video', models.ForeignKey(orm[u'hotspot.video'], null=False)),
            ('videogenre', models.ForeignKey(orm[u'hotspot.videogenre'], null=False))
        ))
        db.create_unique(m2m_table_name, ['video_id', 'videogenre_id'])

        # Adding M2M table for field comments_m2m on 'Video'
        m2m_table_name = db.shorten_name('hot_spot_video_comments_m2m')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('video', models.ForeignKey(orm[u'hotspot.video'], null=False)),
            ('comments_of_video', models.ForeignKey(orm[u'hotspot.comments_of_video'], null=False))
        ))
        db.create_unique(m2m_table_name, ['video_id', 'comments_of_video_id'])

        # Adding model 'TvChannels'
        db.create_table('hot_spot_tv_channels', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('channel_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('channel_name_eng', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'hotspot', ['TvChannels'])

        # Adding model 'TvForecastSources'
        db.create_table('hot_spot_tv_forecast_sources', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'hotspot', ['TvForecastSources'])

        # Adding model 'TvForecast'
        db.create_table('hot_spot_tv_forecast', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.TvForecastSources'])),
            ('channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hotspot.TvChannels'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('time_hour', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('time_minute', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=2000, null=True)),
            ('date_get', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'hotspot', ['TvForecast'])


    def backwards(self, orm):
        # Deleting model 'IPPool'
        db.delete_table(u'hotspot_ippool')

        # Deleting model 'IPInUse'
        db.delete_table(u'hotspot_ipinuse')

        # Deleting model 'Games_Section'
        db.delete_table(u'hotspot_games_section')

        # Deleting model 'Games'
        db.delete_table(u'hotspot_games')

        # Removing M2M table for field section_game on 'Games'
        db.delete_table(db.shorten_name(u'hotspot_games_section_game'))

        # Deleting model 'Nas'
        db.delete_table('nas_nas')

        # Deleting model 'Prefecturs'
        db.delete_table('prefecturs')

        # Deleting model 'DistrictAdministration'
        db.delete_table('district_administration')

        # Deleting model 'HomeAdministration'
        db.delete_table('home_administration')

        # Deleting model 'HotSpotRate'
        db.delete_table('hot_spot_rate')

        # Deleting model 'HotSpotWeatger'
        db.delete_table('hot_spot_weather')

        # Deleting model 'HotSpotQueryStatistic'
        db.delete_table('hot_spot_query_statistic')

        # Deleting model 'HotSpotReview'
        db.delete_table('hot_spot_review')

        # Deleting model 'MainNews'
        db.delete_table('hot_spot_main_news')

        # Deleting model 'WeatherCountries'
        db.delete_table('hot_spot_weather_countries')

        # Deleting model 'MobiWeather'
        db.delete_table('hot_spot_mobi_weather')

        # Deleting model 'MobiOrganizationsUnique'
        db.delete_table('hot_spot_mobi_organizations_unique')

        # Deleting model 'MobiOrganizationsUserChanges'
        db.delete_table('hot_spot_mobi_organization_user_changes')

        # Deleting model 'VideoGenre'
        db.delete_table('hot_spot_video_genre')

        # Deleting model 'Video_Rate'
        db.delete_table('rate_video')

        # Deleting model 'Comments_Of_Video'
        db.delete_table('hotspot_video_comments')

        # Deleting model 'HotSpot_Bad_Video_Link'
        db.delete_table('hot_spot_bad_video_link')

        # Deleting model 'Video'
        db.delete_table('hot_spot_video')

        # Removing M2M table for field genres on 'Video'
        db.delete_table(db.shorten_name('hot_spot_video_genres'))

        # Removing M2M table for field comments_m2m on 'Video'
        db.delete_table(db.shorten_name('hot_spot_video_comments_m2m'))

        # Deleting model 'TvChannels'
        db.delete_table('hot_spot_tv_channels')

        # Deleting model 'TvForecastSources'
        db.delete_table('hot_spot_tv_forecast_sources')

        # Deleting model 'TvForecast'
        db.delete_table('hot_spot_tv_forecast')


    models = {
        u'billing.billserviceaccount': {
            'Meta': {'object_name': 'BillserviceAccount', 'db_table': "u'billservice_account'"},
            'address': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'allow_expresscards': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_webcab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'assigned_to': ('django.db.models.fields.IntegerField', [], {}),
            'auto_paid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'balance_blocked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ballance': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '14', 'decimal_places': '2'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contactperson': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contactperson_phone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'contract': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'credit': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '20', 'decimal_places': '2'}),
            'disabled_by_limit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'elevator_direction': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'entrance': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'fullname': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'group_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'house': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'house_bulk': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idle_time': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'idle_time_for_every_month': ('django.db.models.fields.IntegerField', [], {'default': '15'}),
            'idle_time_for_internet': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'notification_balance': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'passport': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'passport_date': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'passport_given': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'phone_h': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'phone_m': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prices_group_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'row': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'suspended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'vlan': ('django.db.models.fields.IntegerField', [], {})
        },
        u'data_centr.price': {
            'Meta': {'object_name': 'Price'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'data_centr.service_type': {
            'Meta': {'object_name': 'Service_type'},
            'about': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'data_centr.tariff': {
            'Meta': {'object_name': 'Tariff'},
            'about': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'archive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'billing_tariff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.Tariff']", 'null': 'True', 'blank': 'True'}),
            'cpu': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'depth': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'electricity': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'equipment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'for_person': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['internet.Internet_persons_for_connection']", 'null': 'True', 'blank': 'True'}),
            'free_minutes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'garant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hdd': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ip': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'port': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'price_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_centr.Price']"}),
            'ram': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'section_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'service_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_centr.Service_type']"}),
            'socket': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'speed_inet': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'tel_zone': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tower_casing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hotspot.activesession': {
            'Meta': {'object_name': 'ActiveSession', 'db_table': "'radius_activesession'", 'managed': 'False'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'hotspot_activesession_acc'", 'null': 'True', 'to': u"orm['billing.BillserviceAccount']"}),
            'acct_terminate_cause': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'bytes_in': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bytes_out': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'caller_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'framed_ip_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'framed_protocol': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interrim_update': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'nas_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nas_int': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'hotspot_nas'", 'null': 'True', 'to': u"orm['hotspot.Nas']"}),
            'session_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'session_time': ('django.db.models.fields.IntegerField', [], {}),
            'sessionid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'speed_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subaccount': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'hotspot_activesession_sub'", 'null': 'True', 'to': u"orm['internet.SubAccount']"})
        },
        u'hotspot.comments_of_video': {
            'Meta': {'object_name': 'Comments_Of_Video', 'db_table': "'hotspot_video_comments'"},
            'add_to_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment_content': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'commentator_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hotspot.districtadministration': {
            'Meta': {'object_name': 'DistrictAdministration', 'db_table': "'district_administration'"},
            'add_information': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'adress': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'prefecturs': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.Prefecturs']", 'null': 'True', 'blank': 'True'}),
            'subway_station': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'tel_numbers': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'web_site': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'x': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'y': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        u'hotspot.games': {
            'Meta': {'ordering': "['game_name']", 'object_name': 'Games'},
            'banner': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'game_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'http': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'section': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'section2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'section_game': ('django.db.models.fields.related.ManyToManyField', [], {'default': '1', 'to': u"orm['hotspot.Games_Section']", 'symmetrical': 'False'})
        },
        u'hotspot.games_section': {
            'Meta': {'object_name': 'Games_Section'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'hotspot.homeadministration': {
            'Meta': {'object_name': 'HomeAdministration', 'db_table': "'home_administration'"},
            'add_information': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'adress': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'district_administration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.DistrictAdministration']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'subway_station': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'tel_numbers': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'web_site': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'x': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'y': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        u'hotspot.hotspot_bad_video_link': {
            'Meta': {'object_name': 'HotSpot_Bad_Video_Link', 'db_table': "'hot_spot_bad_video_link'"},
            'broken_video_id': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'contact_face': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'hotspot.hotspotquerystatistic': {
            'Meta': {'object_name': 'HotSpotQueryStatistic', 'db_table': "'hot_spot_query_statistic'"},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query_string': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'})
        },
        u'hotspot.hotspotrate': {
            'Meta': {'object_name': 'HotSpotRate', 'db_table': "'hot_spot_rate'"},
            'char_code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'nominal': ('django.db.models.fields.IntegerField', [], {'max_length': '512'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        u'hotspot.hotspotreview': {
            'Meta': {'object_name': 'HotSpotReview', 'db_table': "'hot_spot_review'"},
            'adres': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'contact_face': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'telnumber': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'was_treated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'hotspot.hotspotweatger': {
            'Meta': {'object_name': 'HotSpotWeatger', 'db_table': "'hot_spot_weather'"},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'spr_class': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'temp_d_n': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'temp_now': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        u'hotspot.ipinuse': {
            'Meta': {'object_name': 'IPInUse'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'disabled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.IPPool']"})
        },
        u'hotspot.ippool': {
            'Meta': {'ordering': "['name']", 'object_name': 'IPPool'},
            'end_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'next_ippool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.IPPool']", 'null': 'True', 'blank': 'True'}),
            'start_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hotspot.mainnews': {
            'Meta': {'object_name': 'MainNews', 'db_table': "'hot_spot_main_news'"},
            'date_get_news': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'discription_news': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_news': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'img_news_root': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'link_news': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'news_type': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'portal_copyright': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'portal_diskription': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'portal_link': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'portal_name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'title_news': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        u'hotspot.mobiorganizationsunique': {
            'Meta': {'object_name': 'MobiOrganizationsUnique', 'db_table': "'hot_spot_mobi_organizations_unique'"},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'equal_coord_range': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'hours': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'org_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'org_type': ('django.db.models.fields.IntegerField', [], {}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'x': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '16', 'decimal_places': '10', 'blank': 'True'}),
            'y': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '16', 'decimal_places': '10', 'blank': 'True'}),
            'yan_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'hotspot.mobiorganizationsuserchanges': {
            'Meta': {'object_name': 'MobiOrganizationsUserChanges', 'db_table': "'hot_spot_mobi_organization_user_changes'"},
            'applied': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'org_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.MobiOrganizationsUnique']"}),
            'to_del': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'u_address': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'u_hours': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'u_org_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'u_phone': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'u_url': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'user_email': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        u'hotspot.mobiweather': {
            'Meta': {'object_name': 'MobiWeather', 'db_table': "'hot_spot_mobi_weather'"},
            'city_weather_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.WeatherCountries']", 'null': 'True', 'blank': 'True'}),
            'cloud': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_date_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'humidity': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pressure': ('django.db.models.fields.FloatField', [], {}),
            'source_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'taking_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'temp_from': ('django.db.models.fields.FloatField', [], {}),
            'temp_to': ('django.db.models.fields.FloatField', [], {}),
            'wind_dir': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'wind_speed': ('django.db.models.fields.FloatField', [], {})
        },
        u'hotspot.nas': {
            'Meta': {'object_name': 'Nas', 'db_table': "'nas_nas'"},
            'acct_interim_interval': ('django.db.models.fields.IntegerField', [], {'default': '60', 'null': 'True', 'blank': 'True'}),
            'allow_ipn': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_pppoe': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_pptp': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'confstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'data_centr_tarif': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['data_centr.Tariff']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identify': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ipaddress': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ipn_speed_action': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'reset_action': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'snmp_version': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'speed_attr_id1': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'speed_attr_id2': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'speed_value1': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'speed_value2': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'speed_vendor_1': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'speed_vendor_2': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'subacc_add_action': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'subacc_delete_action': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'subacc_disable_action': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'subacc_enable_action': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'subacc_ipn_speed_action': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'mikrotik3'", 'max_length': '32'}),
            'user_add_action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_delete_action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_disable_action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_enable_action': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vpn_speed_action': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        u'hotspot.prefecturs': {
            'Meta': {'object_name': 'Prefecturs', 'db_table': "'prefecturs'"},
            'add_information': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'adress': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512'}),
            'subway_station': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'tel_numbers': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'web_site': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'x': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'y': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'hotspot.tvchannels': {
            'Meta': {'object_name': 'TvChannels', 'db_table': "'hot_spot_tv_channels'"},
            'channel_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'channel_name_eng': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hotspot.tvforecast': {
            'Meta': {'object_name': 'TvForecast', 'db_table': "'hot_spot_tv_forecast'"},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.TvChannels']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'date_get': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.TvForecastSources']"}),
            'time_hour': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'time_minute': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'hotspot.tvforecastsources': {
            'Meta': {'object_name': 'TvForecastSources', 'db_table': "'hot_spot_tv_forecast_sources'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hotspot.video': {
            'Meta': {'object_name': 'Video', 'db_table': "'hot_spot_video'"},
            'age_restrictions': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'budget': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cast': ('django.db.models.fields.CharField', [], {'max_length': '600', 'blank': 'True'}),
            'comments_m2m': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['hotspot.Comments_Of_Video']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'date_aded': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '6000', 'blank': 'True'}),
            'director': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['hotspot.VideoGenre']", 'null': 'True', 'blank': 'True'}),
            'genres_client_view': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_gid_film': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'image_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'imdb_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'imdb_rating': ('django.db.models.fields.CharField', [], {'max_length': '600', 'null': 'True', 'blank': 'True'}),
            'internal_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'kp_rating': ('django.db.models.fields.CharField', [], {'max_length': '600', 'null': 'True', 'blank': 'True'}),
            'label_text': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '50000', 'blank': 'True'}),
            'one_serial_links': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '50000', 'blank': 'True'}),
            'orig_title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'player_video_url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '9200'}),
            'premiere_date': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'quality': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rating_by': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'screenplay': ('django.db.models.fields.CharField', [], {'max_length': '600', 'blank': 'True'}),
            'site_rating': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hotspot.Video_Rate']", 'null': 'True', 'blank': 'True'}),
            'sound': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'source': ('django.db.models.fields.IntegerField', [], {}),
            'time': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'translit_video_name': ('django.db.models.fields.CharField', [], {'max_length': '400', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'video_type': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'hotspot.video_rate': {
            'Meta': {'object_name': 'Video_Rate', 'db_table': "'rate_video'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rating_score': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'rating_votes': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'hotspot.videogenre': {
            'Meta': {'object_name': 'VideoGenre', 'db_table': "'hot_spot_video_genre'"},
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'translit_genre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'hotspot.weathercountries': {
            'Meta': {'object_name': 'WeatherCountries', 'db_table': "'hot_spot_weather_countries'"},
            'city_eng_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city_rus_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country_eng_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country_rus_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'openweathermap_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'region_id': ('django.db.models.fields.IntegerField', [], {}),
            'yandex_city_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'internet.accessparameters': {
            'Meta': {'object_name': 'AccessParameters', 'db_table': "'billservice_accessparameters'"},
            'access_time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.TimePeriod']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'access_type': ('django.db.models.fields.CharField', [], {'default': "'PPTP'", 'max_length': '255', 'blank': 'True'}),
            'burst_rx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'burst_time_rx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'burst_time_tx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'burst_treshold_rx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'burst_treshold_tx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'burst_tx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn_for_vpn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_rx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'max_tx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'min_rx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'min_tx': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '8', 'blank': 'True'}),
            'sessionscount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'internet.internet_persons_for_connection': {
            'Meta': {'object_name': 'Internet_persons_for_connection', 'db_table': "'internet_persons_for_connection'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'persons': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'internet.ipinuse': {
            'Meta': {'ordering': "['ip']", 'object_name': 'IPInUse', 'db_table': "'billservice_ipinuse'"},
            'ack': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'disabled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dynamic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.IPPool']"})
        },
        u'internet.ippool': {
            'Meta': {'ordering': "['name']", 'object_name': 'IPPool', 'db_table': "'billservice_ippool'"},
            'end_ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'next_ippool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.IPPool']", 'null': 'True', 'blank': 'True'}),
            'start_ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'internet.radiustraffic': {
            'Meta': {'object_name': 'RadiusTraffic', 'db_table': "'billservice_radiustraffic'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prepaid_direction': ('django.db.models.fields.IntegerField', [], {'default': '2', 'blank': 'True'}),
            'prepaid_value': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'reset_prepaid_traffic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rounding': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'tarification_step': ('django.db.models.fields.IntegerField', [], {'default': '1024', 'blank': 'True'})
        },
        u'internet.settlementperiod': {
            'Meta': {'ordering': "['name']", 'object_name': 'SettlementPeriod', 'db_table': "'billservice_settlementperiod'"},
            'autostart': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'length_in': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'internet.subaccount': {
            'Meta': {'ordering': "['-username']", 'object_name': 'SubAccount', 'db_table': "'billservice_subaccount'"},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['billing.BillserviceAccount']", 'null': 'True', 'blank': 'True'}),
            'allow_addonservice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_dhcp_with_block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_dhcp_with_minus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_dhcp_with_null': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_ipn_with_block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_ipn_with_minus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_ipn_with_null': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_mac_update': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_vpn_with_block': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_vpn_with_minus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_vpn_with_null': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'associate_pppoe_ipn_mac': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'associate_pptp_ipn_ip': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn_added': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ipn_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ipn_ip_address': ('django.db.models.fields.TextField', [], {'default': "'0.0.0.0'", 'null': 'True', 'blank': 'True'}),
            'ipn_ipinuse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subaccount_ipn_ipinuse_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['internet.IPInUse']"}),
            'ipn_ipv6_ip_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ipn_mac_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '17', 'blank': 'True'}),
            'ipn_sleep': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ipn_speed': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ipv4_ipn_pool': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subaccount_ipn_ippool_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['internet.IPPool']", 'blank': 'True', 'null': 'True'}),
            'ipv4_vpn_pool': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subaccount_vpn_ippool_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['internet.IPPool']", 'blank': 'True', 'null': 'True'}),
            'ipv6_vpn_pool': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subaccount_ipv6_vpn_ippool_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['internet.IPPool']", 'blank': 'True', 'null': 'True'}),
            'nas_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'need_resync': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sessionscount': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'speed': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'switch_port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text_password': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'vlan': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'vpn_ip_address': ('django.db.models.fields.IPAddressField', [], {'default': "'0.0.0.0'", 'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'vpn_ipinuse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subaccount_vpn_ipinuse_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['internet.IPInUse']"}),
            'vpn_ipv6_ip_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'vpn_ipv6_ipinuse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subaccount_vpn_ipv6_ipinuse_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['internet.IPInUse']"}),
            'vpn_speed': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'internet.tariff': {
            'Meta': {'ordering': "['name']", 'object_name': 'Tariff', 'db_table': "'billservice_tariff'"},
            'access_parameters': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.AccessParameters']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_ballance_transfer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_express_pay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_userblock': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'ps_null_ballance_checkout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'radius_traffic_transmit_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.RadiusTraffic']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'require_tarif_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reset_tarif_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'settlement_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.SettlementPeriod']", 'null': 'True', 'blank': 'True'}),
            'time_access_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.TimeAccessService']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'traffic_transmit_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['internet.TrafficTransmitService']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'userblock_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '30', 'decimal_places': '2', 'blank': 'True'}),
            'userblock_max_days': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'userblock_require_balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'vpn_guest_ippool': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tariff_guest_vpn_ippool_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['internet.IPPool']"}),
            'vpn_ippool': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tariff_vpn_ippool_set'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['internet.IPPool']"})
        },
        u'internet.timeaccessservice': {
            'Meta': {'object_name': 'TimeAccessService', 'db_table': "'billservice_timeaccessservice'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prepaid_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'reset_time': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rounding': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'tarification_step': ('django.db.models.fields.IntegerField', [], {'default': '60', 'blank': 'True'})
        },
        u'internet.timeperiod': {
            'Meta': {'ordering': "['name']", 'object_name': 'TimePeriod', 'db_table': "'billservice_timeperiod'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'internet.traffictransmitservice': {
            'Meta': {'object_name': 'TrafficTransmitService', 'db_table': "'billservice_traffictransmitservice'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reset_traffic': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['hotspot']