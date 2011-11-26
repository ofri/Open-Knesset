#encoding: utf-8
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class Video(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=2000)
    embed_link = models.URLField(max_length=1000, verify_exists=False)
    image_link = models.URLField(max_length=1000, verify_exists=False)
    link = models.URLField(max_length=1000, verify_exists=False)
    source_type = models.CharField(max_length=50)
    source_id = models.CharField(max_length=255)
    group = models.CharField(max_length=20)
    content_type = models.ForeignKey(ContentType)
    object_pk = models.TextField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

