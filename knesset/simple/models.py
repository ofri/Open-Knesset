from django.db import models
from django.db.models import Q


class Correlation(models.Model):
    m1 = models.ForeignKey('Member', related_name = 'm1')
    m2 = models.ForeignKey('Member', related_name = 'm2')
    score = models.IntegerField(default=0)
    normalized_score = models.FloatField(null=True)
    not_same_party = models.BooleanField(null=True)
    def __unicode__(self):
        return "%s (%s) - %s (%s) - %.0f" % (self.m1.name,self.m1.parties.all()[0].name,self.m2.name,self.m2.parties.all()[0].name,self.normalized_score)
    

class Topic(models.Model):
    name        = models.CharField(max_length=64)
    description = models.TextField(max_length=2048)
    def __unicode__(self):
        return "%s" % self.name
    

class Party(models.Model):
    name        = models.CharField(max_length=64)
    start_date  = models.DateField(null=True)
    end_date    = models.DateField(null=True)

    def __unicode__(self):
        return "%s" % self.name
    
    def Url(self):
        return "/admin/simple/party/%d" % self.id

    def NameWithLink(self):
        return '<a href="%s">%s</a>' %(self.Url(),self.name)
    NameWithLink.allow_tags = True
    
    def MembersString(self):
        return ", ".join([m.NameWithLink() for m in self.members.all().order_by('name')])
    MembersString.allow_tags = True
    
class Membership(models.Model):
    member      = models.ForeignKey('Member')
    party       = models.ForeignKey('Party')
    start_date  = models.DateField(null=True)
    end_date    = models.DateField(null=True)

    def __unicode__(self):
        return "%s-%s (%s-%s)" % (self.member.name,self.party.name,str(self.start_date),str(self.end_date))

class Member(models.Model):
    name    = models.CharField(max_length=64)
    parties = models.ManyToManyField(Party, related_name='members', through='Membership')
    start_date  = models.DateField(null=True)
    end_date    = models.DateField(null=True)
    def __unicode__(self):
        return "%s" % self.name
    
    def PartiesString(self):
        return ", ".join([p.NameWithLink() for p in self.parties.all().order_by('membership__start_date')])
    PartiesString.allow_tags = True
    
    def TotalVotesCount(self):
        return self.for_votes.count()+self.against_votes.count()+self.abstain_votes.count()
    
    def ForVotesCount(self):
        return self.for_votes.count()

    def AgainstVotesCount(self):
        return self.against_votes.count()

    def AbstainVotesCount(self):
        return self.abstain_votes.count()
    
    def NoVotesCount(self):
        return self.no_votes.count()
    
    
    def LowestCorrelations(self):
        return Correlation.objects.all().filter(Q(m1=self.id)|Q(m2=self.id)).order_by('normalized_score')[0:5]
    
    def HighestCorrelations(self):
        return Correlation.objects.all().filter(Q(m1=self.id)|Q(m2=self.id)).order_by('-normalized_score')[0:5]
    
    def CorrelationListToString(self,cl):
        
        strings = []
        for c in cl:
            if c.m1 == self:
                m = c.m2
            else:
                m = c.m1
            strings.append("%s (%.0f)"%(m.NameWithLink(),c.normalized_score))
        return ", ".join(strings)
    
    
    def Url(self):
        return "/admin/simple/member/%d" % self.id

    def NameWithLink(self):
        return '<a href="%s">%s</a>' %(self.Url(),self.name)
    NameWithLink.allow_tags = True    

class Vote(models.Model):
    title         = models.CharField(max_length=1000)
    time          = models.DateTimeField(null=True,blank=True)
    time_string   = models.CharField(max_length=100)
    voted_for     = models.ManyToManyField(Member, related_name='for_votes', blank=True)
    voted_against = models.ManyToManyField(Member, related_name='against_votes', blank=True)
    voted_abstain = models.ManyToManyField(Member, related_name='abstain_votes', blank=True)
    didnt_vote    = models.ManyToManyField(Member, related_name='no_votes', blank=True)
    
    topics_for     = models.ManyToManyField(Topic, related_name='for_votes', blank=True)
    topics_against = models.ManyToManyField(Topic, related_name='against_votes', blank=True)
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.time_string)
