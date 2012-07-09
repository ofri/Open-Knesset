from django.db import models
from django.utils import simplejson as json

class DocumentManager(models.Manager):
    def from_json(j):
        """Read a json j, and create Document instances based on it"""
        raise Exception('Not Implemented Yet')

class Document(models.Model):
    title = models.CharField(max_length=2000)
    url = models.URLField()
    publication_date = models.DateField(blank=True, null=True)
    # requesting committees
    req_committees = models.ManyToManyField('committees.Committee',
                                            related_name='mmm_documents',
                                            blank=True, null=True)
    # requesting members
    req_mks = models.ManyToManyField('mks.Member',
                                     related_name='mmm_documents',
                                     blank=True, null=True)
    author_names = models.CharField(max_length=500, blank=True)

    objects = DocumentManager()

    def __unicode__(self):
        return self.title
