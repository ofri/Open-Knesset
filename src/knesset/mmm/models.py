from django.db import models
from knesset.mks.models import Member
from knesset.committee.models import Committee
import simplejson 
import re
import logging

logger = logging.getLogger("open-knesset.mmm.models")

def parse_json(j):
    """ recieves json from mmm-scraping project, loads/parses and returns list of dictionaries """
    
    result = simplejson.load(j)
    
    # parsing textual parts
    for o in result:
        o['candidates'] = re.sub(r"\s+", r" " , " ".join(o['candidates']))
    
    return result



def text_lookup(modelName, text):
    """ recieves a text and a modelName and returns a list of modelName objects found in it"""
    
    result = []
    
    # a list of all modelName objects
    all_obj = [(m, m.name) for m in modelName.objects.all()]
    
    for k, v in all_obj:
        if v in text:
            result.append(k)
    
    return result


class Document(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=2000)
    publication_date = models.DateField(blank=True, null=True)
    # requesting committee
    req_committee = models.ManyToManyField(Committee,
                                            related_name='mmm_documents',
                                            blank=True, null=True)
    # requesting members
    req_mks = models.ManyToManyField(Member,
                                     related_name='mmm_documents',
                                     blank=True, null=True)
    author_names = models.CharField(max_length=500, blank=True)

    objects = DocumentManager()
        

    def __unicode__(self):
        return self.title
    

class DocumentManager(models.Manager):
    def from_json(j):
        """Read a json j, and create Document instances based on it"""
        # info from m.m.m site
        info = parse_json(j)
        
        # checking if the db already has document o instance and if no, creating one
        for o in info:
            if self.filter(url=o['url']).exists():
                logger.info("%s already exists in db" % o['url'])
            else:
                logger.info("creating new Document instance: %s" % o['url'])
                mks = text_lookup(Member, o['candidates'])
                committees = text_lookup(Committee, o['candidates'])
                d = self.create(url=o['url'], title=o['title'], publication_date=o['date'],req_committee=committees, req_mks=mks, author_names=o['author'])
