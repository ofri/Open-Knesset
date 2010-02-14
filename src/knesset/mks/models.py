#encoding: utf-8
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


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
    start_date  = models.DateField(blank=True, null=True)
    end_date    = models.DateField(blank=True, null=True)
    is_coalition = models.BooleanField(default=False)
    number_of_members = models.IntegerField(blank=True, null=True)
    number_of_seats = models.IntegerField(blank=True, null=True)
    class Meta:
        verbose_name = _('Party')
        verbose_name_plural = _('Parties')
        ordering = ('-number_of_seats',)

    @property
    def uri_template (self):
        # TODO: use the Site's url from django.contrib.site
        return "%s/api/party/%s/htmldiv/" % ('', self.id)

    def __unicode__(self):
        return "%s" % self.name

    def current_members(self):
        return self.members.filter(is_current=True)

    def past_members(self):
        return self.members.filter(is_current=False)
    
    def name_with_dashes(self):
        return self.name.replace("'",'"').replace(' ','-')
    
    def Url(self):
        return "/admin/simple/party/%d" % self.id

    def NameWithLink(self):
        return '<a href="%s">%s</a>' %(self.Url(),self.name)
    NameWithLink.allow_tags = True
    
    def MembersString(self):
        return ", ".join([m.NameWithLink() for m in self.members.all().order_by('name')])
    MembersString.allow_tags = True

    def member_list(self):
        return self.members.all()

    @models.permalink
    def get_absolute_url(self):
        return ('party-detail-with-slug', [str(self.id), self.name_with_dashes()])

    
class Membership(models.Model):
    member      = models.ForeignKey('Member')
    party       = models.ForeignKey('Party')
    start_date  = models.DateField(blank=True, null=True)
    end_date    = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return "%s-%s (%s-%s)" % (self.member.name,self.party.name,str(self.start_date),str(self.end_date))


class Member(models.Model):
    name    = models.CharField(max_length=64)
    parties = models.ManyToManyField(Party, related_name='members', through='Membership')
    start_date  = models.DateField(blank=True, null=True)
    end_date    = models.DateField(blank=True, null=True)
    img_url     = models.URLField(blank=True)
    phone = models.CharField(blank=True, null=True, max_length=20)
    fax = models.CharField(blank=True, null=True, max_length=20)
    email = models.EmailField(blank=True, null=True)
    website     = models.URLField(blank=True, null=True)
    family_status = models.CharField(blank=True, null=True,max_length=10)
    number_of_children = models.IntegerField(blank=True, null=True)
    date_of_birth  = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(blank=True, null=True, max_length=100)    
    date_of_death  = models.DateField(blank=True, null=True)
    year_of_aliyah = models.IntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Member')
        verbose_name_plural = _('Members')


    def __unicode__(self):
        return "%s" % self.name
    
    def title(self):
        return self.name

    def name_with_dashes(self):
        return self.name.replace(' - ',' ').replace("'","").replace(u"”",'').replace("`","").replace("(","").replace(")","").replace(' ','-')

    def Party(self):    
        return self.parties.all().order_by('-membership__start_date')[0]

    def PartiesString(self):
        return ", ".join([p.NameWithLink() for p in self.parties.all().order_by('membership__start_date')])
    PartiesString.allow_tags = True
    
    def TotalVotesCount(self):
        return self.votes.exclude(voteaction__type='no-vote').count()
    
    def for_votes(self):
        return self.votes.filter(voteaction__type='for')

    def ForVotesCount(self):
        return self.for_votes().count()

    def against_votes(self):
        return self.votes.filter(voteaction__type='against')

    def AgainstVotesCount(self):
        return self.against_votes().count()

    def abstain_votes(self):
        return self.votes.filter(voteaction__type='abstain')
    
    def AbstainVotesCount(self):
        return self.abstain_votes().count()
    
    def no_votes(self):
        return self.votes.filter(voteaction__type='no-vote')
    
    def NoVotesCount(self):
        return self.no_votes().count()
    
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
    
    
    @models.permalink
    def get_absolute_url(self):
        return ('member-detail-with-slug', [str(self.id), self.name_with_dashes()])

    def NameWithLink(self):
        return '<a href="%s">%s</a>' %(self.Url(),self.name)
    NameWithLink.allow_tags = True    

