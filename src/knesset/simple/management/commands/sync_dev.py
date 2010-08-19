# no handling now: posts

from datetime import date
from django.db.models import Q
from django.core.management.base import NoArgsCommand

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from knesset.mks.models import Member,Party
from knesset.laws.models import Law,Bill,PrivateProposal,KnessetProposal,Vote,VoteAction,MemberVotingStatistics,PartyVotingStatistics
from knesset.committees.models import Committee,CommitteeMeeting
from knesset.links.models import Link, LinkType
from knesset.user.models import UserProfile
import tagging
import actstream
import planet


class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
    
        parties = Party.objects.all()

        mk_ids = []
        for p in parties:
            mk_ids.append(p.members.all()[0].id)

        mks = Member.objects.filter(id__in=mk_ids)



        bills = Bill.objects.filter(proposers__in=mks)

        laws = set([bill.law for bill in bills])

        pps = []
        kps = []
        for b in bills:
            pps.extend(b.proposals.all())
            if KnessetProposal.objects.filter(bill=b).count()>0:
                kps.append(b.knesset_proposal)

        for pp in pps:
            laws.add(pp.law)

        for kp in kps:
            laws.add(kp.law)


        votes = list(Vote.objects.filter(bills_pre_votes__in=bills))
        votes.extend(list(Vote.objects.filter(bills_first__in=bills)))
        votes.extend(list(Vote.objects.filter(bill_approved__in=bills)))
        vote_actions = VoteAction.objects.filter(member__in=mks, vote__in=votes)

        cms = CommitteeMeeting.objects.filter(mks_attended__in=mks, date__gt=date(2010,05,01), date__lt=date(2010,05,05)).distinct('id')
        committees = set([cm.committee for cm in cms])

        tags = tagging.models.Tag.objects.usage_for_queryset(bills)
        tagged_items = tagging.models.TaggedItem.objects.filter(Q(tag__in=tags, object_id__in=[bill.id for bill in bills])|
                                                                Q(tag__in=tags, object_id__in=[vote.id for vote in votes]))

        mk_ct = ContentType.objects.get_for_model(Member)
        vote_ct = ContentType.objects.get_for_model(Vote)
        links = list(Link.objects.filter(content_type=mk_ct,object_pk__in=[mk.id for mk in mks]))
        links.extend(list(Link.objects.filter(content_type=vote_ct, object_pk__in=[vote.id for vote in votes])))

        actions = actstream.models.Action.objects.filter(actor_object_id__in=mk_ids, 
                                                         actor_content_type=mk_ct, 
                                                         timestamp__gt=date(2010,05,01), 
                                                         timestamp__lt=date(2010,05,20))

        comments = Comment.objects.all()
        users = set([c.user for c in comments])
        user_profiles = UserProfile.objects.filter(user__in=users)


        blogs = planet.models.Blog.objects.filter(member__in=mks)
        feeds = planet.models.Feed.objects.filter(blog__in=blogs)
        posts = planet.models.Post.objects.filter(feed__in=feeds)
        generators = set([feed.generator for feed in feeds])

        ContentType.objects.using('dev').all().delete()
        for ct in ContentType.objects.all():
            ct.save(using='dev')


        for mk in mks:
            mvs = MemberVotingStatistics.objects.get(member=mk)
            mk.user = None
            mk.save(using='dev')
            mvs.save(using='dev')


        for p in parties:
            pvs = PartyVotingStatistics.objects.get(party=p)
            p.save(using='dev')
            pvs.save(using='dev')


        for bill in bills:
            proposers = bill.proposers.filter(id__in=[mk.id for mk in mks])
            bill.save(using='dev')
            for mk in proposers:
                bill.proposers.add(Member.objects.using('dev').get(pk=mk.id))


        for law in laws:
            law.save(using='dev')


        for pp in pps:
            proposers = pp.proposers.filter(id__in=[mk.id for mk in mks])
            pp.save(using='dev')
            for mk in proposers:
                pp.proposers.add(Member.objects.using('dev').get(pk=mk.id))


        for kp in kps:
            kp.save(using='dev')


        for vote in votes:
            b = vote.bills_pre_votes.all()
            vote.save(using='dev')
            for bill in b:
                if bill in bills:
                    vote.bills_pre_votes.add(Bill.objects.using('dev').get(pk=bill.id))


        for va in vote_actions:
            va.save(using='dev')


        for committee in committees:
            committee.save(using='dev')


        for cm in cms:
            attended = cm.mks_attended.filter(id__in=[mk.id for mk in mks])
            cm.save(using='dev')
            for mk in attended:
                cm.mks_attended.add(Member.objects.using('dev').get(pk=mk.id))
            
            cm.save(using='dev')


        for tag in tags:
            tag.save(using='dev')


        for ti in tagged_items:
            ti.save(using='dev')


        for link in links:
            lt = link.link_type
            link.save(using='dev')
            if lt:
                lt.save(using='dev')


        for a in actions:
            a.save(using='dev')


        for c in comments:
            c.save(using='dev')


        for u in users:
            u.set_password('123456')
            u.save(using='dev')


        for up in user_profiles:
            up.save(using='dev')


        for blog in blogs:
            blog.save(using='dev')
        
        for feed in feeds:
            # feed.objects.using('dev').save(using='dev') # can't beacuse of planet
            feed._state.db = 'dev'
            feed.save()

        for generator in generators:
            generator.save(using='dev')
            
        
        for post in posts:
            post.save(using='dev')
