# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.filter(app_label='badges').delete()

    def backwards(self, orm):
        pass

    models = {

    }

    complete_apps = ['badges']
