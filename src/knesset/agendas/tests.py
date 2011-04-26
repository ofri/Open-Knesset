import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import translation
from django.conf import settings

from models import Agenda, AgendaVote
from knesset.laws.models import Vote, VoteAction
from knesset.mks.models import Party, Member

just_id = lambda x: x.id

class SimpleTest(TestCase):
    def setUp(self):
        self.party_1 = Party.objects.create(name='party 1')
        self.mk_1 = Member.objects.create(name='mk_1',
                                          start_date=datetime.date(2010,1,1),
                                          current_party=self.party_1)
        self.user_1 = User.objects.create_user('jacob', 'jacob@jacobian.org', 'JKM')
        self.user_2 = User.objects.create_user('john', 'lennon@thebeatles.com', 'LSD')
        self.user_3 = User.objects.create_user('superman', 'super@user.com', 'CRP')
        self.user_3.is_superuser = True
        self.user_3.save()
        
        self.agenda_1 = Agenda.objects.create(name='agenda 1',
                                              description='a bloody good agenda 1',
                                              public_owner_name='Dr. Jacob',
                                              is_public=True)
        self.agenda_2 = Agenda.objects.create(name='agenda 2',
                                              description='a bloody good agenda 2',
                                              public_owner_name='Greenpeace',
                                              is_public=True)
        self.agenda_3 = Agenda.objects.create(name='agenda 3',
                                              description='a bloody good agenda 3',
                                              public_owner_name='Hidden One',
                                              is_public=False)
        self.agenda_1.editors = [self.user_1]
        self.agenda_2.editors = [self.user_1, self.user_2]
        self.agenda_3.editors = [self.user_2]
        self.vote_1 = Vote.objects.create(title='vote 1',time=datetime.datetime.now())
        self.vote_2 = Vote.objects.create(title='vote 2',time=datetime.datetime.now())
        self.voteaction_1 = VoteAction.objects.create(vote=self.vote_1, member=self.mk_1, type='for')
        self.voteaction_2 = VoteAction.objects.create(vote=self.vote_2, member=self.mk_1, type='for')
        self.agendavote_1 = AgendaVote.objects.create(agenda=self.agenda_1,
                                                      vote=self.vote_1,
                                                      score=-1,
                                                      reasoning="there's got to be a reason 1")
        self.agendavote_2 = AgendaVote.objects.create(agenda=self.agenda_2,
                                                      vote=self.vote_2,
                                                      score=0.5,
                                                      reasoning="there's got to be a reason 2")
        self.agendavote_3 = AgendaVote.objects.create(agenda=self.agenda_1,
                                                      vote=self.vote_2,
                                                      score=0.5,
                                                      reasoning="there's got to be a reason 3")
        
        self.domain = 'http://' + Site.objects.get_current().domain
    
    def testAgendaList(self):
        translation.activate(settings.LANGUAGE_CODE)
        # test anonymous user
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.agenda_1.id, self.agenda_2.id, ])
        
        # test logged in user 1
        self.assertTrue(self.client.login(username='jacob', password='JKM'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.agenda_1.id, self.agenda_2.id, ])
        
        # test logged in user 2
        self.assertTrue(self.client.login(username='superman', password='CRP'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.agenda_1.id, self.agenda_2.id, self.agenda_3.id])
        
        # test logged in as superuser
        self.assertTrue(self.client.login(username='john', password='LSD'))
        res = self.client.get(reverse('agenda-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/agenda_list.html')
        object_list = res.context['object_list']
        self.assertEqual(map(just_id, object_list), 
                         [ self.agenda_1.id, self.agenda_2.id, self.agenda_3.id])
        
        translation.deactivate()
        
    def testAgendaDetail(self):
        
        # Access public agenda while not logged in
        res = self.client.get(reverse('agenda-detail', 
                                      kwargs={'object_id': self.agenda_1.id}))
        self.assertTemplateUsed(res,
                                'agendas/agenda_detail.html')
        self.assertEqual(res.context['object'].id, self.agenda_1.id)
        self.assertEqual(res.context['object'].description, self.agenda_1.description)
        self.assertEqual(res.context['object'].public_owner_name, self.agenda_1.public_owner_name)
        self.assertEqual(list(res.context['object'].editors.all()), [self.user_1])

    def testAgendaMkDetail(self):
        res = self.client.get(reverse('mk-agenda-detail', 
                                      kwargs={'object_id': self.agenda_1.id,
                                              'member_id': self.mk_1.id}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'agendas/mk_agenda_detail.html')
        self.assertEqual(int(res.context['score']), -33)
        self.assertEqual(len(res.context['related_votes']), 2)
        
        
    def tearDown(self):
        self.party_1.delete()
        self.mk_1.delete()
        self.user_1.delete()
        self.user_2.delete()
        self.user_3.delete()        
        self.vote_1.delete()
        self.vote_2.delete()
        self.agenda_1.delete()
        self.agenda_2.delete()
        self.agenda_3.delete()
