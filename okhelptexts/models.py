from django.db import models


class Helptext(models.Model):
    fulltext = models.TextField()
    moreinfo = models.CharField(max_length=200, default="", blank=True)

    def __unicode__(self):
        return self.fulltext


class Keyword(models.Model):
    helptext = models.ForeignKey(Helptext)
    kw_text = models.CharField(max_length=200)

    def __unicode__(self):
        return self.kw_text
