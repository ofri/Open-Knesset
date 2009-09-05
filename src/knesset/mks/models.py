from django.db import models

from django.db.models import Q


class Correlation(models.Model):
    m1 = models.ForeignKey('Member', related_name = 'm1')
    m2 = models.ForeignKey('Member', related_name = 'm2')
    score = models.IntegerField(default=0)
    normalized_score = models.FloatField(null=True)
    not_same_party = models.NullBooleanField()
    def __unicode__(self):
        return "%s (%s) - %s (%s) - %.0f" % (self.m1.name,self.m1.parties.all()[0].name,self.m2.name,self.m2.parties.all()[0].name,self.normalized_score)
    
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
        return self.votes.exclude(voteaction__type='no-vote').count()
    
    def ForVotesCount(self):
        return self.votes.filter(voteaction__type='for').count()

    def AgainstVotesCount(self):
        return self.votes.filter(voteaction__type='against').count()

    def AbstainVotesCount(self):
        return self.votes.filter(voteaction__type='abstain').count()
    
    def NoVotesCount(self):
        return self.votes.filter(voteaction__type='no-vote').count()
    
    
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

