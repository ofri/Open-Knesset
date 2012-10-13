import logging

from django.db import models
from django.utils import simplejson

from knesset.mks.models import Member
from knesset.committees.models import Committee
from fuzzy_match import fuzzy_match


logger = logging.getLogger("open-knesset.mmm.models")

def text_lookup(Model, text):
    """receives a text and a Model and returns a list of Model objects found in the text"""
    
    result = []

    for m in Model.objects.all():
        if m.name in text:
            result.append(m.id)
        else:
            if fuzzy_match(m.name, text):
                logger.warning('No exact match found. Performing fuzzy matching!')
                result.append(m.id)
    
    return result

#from json helper function
def verify(o, i, mks, committees):
    if i[0].title == o['title'] and i[0].publication_date == o['date'] and i[0].author_names == o['author']:
        if i[0].req_mks == mks or i[0].req_committees == committees:
            logger.info("%s already exists in db" % o['url'])
            return False
        else:
            logger.info("Found differences between imported data and our db. Performing Update!")
            return True
    else:
        logger.warning("Failed DB verification! Encountered multiple conflicts between the object in our db and imported data.")
        return False


class DocumentManager(models.Manager):

    def from_json(self, j):

        # checking if the db already has document o instance and if no, creating one
        for o in j:
            
            i = self.filter(url=o['url'])
            mks = text_lookup(Member, o['heading'])
            committees = text_lookup(Committee, o['heading'])
            
            # db verification
            if i:
                if len(i) != 1:
                    logger.warning("Corrupted DB! More than one object were found with same url.")
                else:
                   if verify(o, i, mks, committees):
                       i.req_mks = mks
                       i.req_committee = committees
            else:
                logger.info("Creating new Document instance: %s" % o['url'])
                d = self.create(url=o['url'], title=o['title'], publication_date=o['date'], author_names=o['author'])
                d.req_committee = committees
                d.req_mks = mks



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
    

