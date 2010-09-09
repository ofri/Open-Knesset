import sys
sys.path[0:0] = [
  '/home/adam/Projects/oknesset/Open-Knesset/src',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/djangorecipe-0.20-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/zc.recipe.egg-1.2.2-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/zc.buildout-1.4.3-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_extensions-0.5-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_piston-0.2.2-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_planet-0.1001-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_pagination-1.0.7-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/PIL-1.1.7-py2.6-linux-i686.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/feedparser-4.1-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_debug_toolbar-0.8.3-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/pyth-0.5.5-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/South-0.7.1-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_haystack-1.0.1_final-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/Whoosh-0.3.18-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/simplejson-2.1.1-py2.6-linux-i686.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/django_tagging-0.3.1-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/oauth-1.0.1-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/python_yadis-1.1.0-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/python_openid-2.2.4-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/eggs/setuptools-0.6c11-py2.6.egg',
  '/home/adam/Projects/oknesset/Open-Knesset/parts/django',
  '/home/adam/Projects/oknesset/Open-Knesset',
  '/home/adam/Projects/oknesset/Open-Knesset/parts/atompub',
  '/home/adam/Projects/oknesset/Open-Knesset/parts/activity_stream',
  ]

import json
data = json.loads(file("tags.json").read())

tags = [ [ x['pk'], x['fields']['name'] ] for x in data if x['model'] == 'tagging.tag' ]
all_tags = dict(tags)

vote_tags = {}

for x in data:
  if x['model'] == 'tagging.taggeditem':
    if x['fields']['content_type'] == ["laws","vote"]:
      tag =  x["fields"]["tag"]
      vote_tags[tag] = all_tags[tag]

from knesset.mks.models import Member, Party
from knesset.laws.models import Vote, VoteAction

print ",",",".join( [x.name.encode("utf8") for x in Party.objects.all()] )

pty_members = {}

for p in Party.objects.all():
  pty_members[p.pk] = 0

for m in Member.objects.all():
  if m.current_party != None:
    pty_members[m.current_party.pk] += 1

for mytag_pk,tagname in vote_tags.iteritems():

  votes = []

  for x in data:
    if x['model'] == 'tagging.taggeditem':
      if x['fields']['content_type'] == ["laws","vote"]:
        tag =  x["fields"]["tag"]
        if tag == mytag_pk:
          votes.append(x["fields"]["object_id"])

  #print votes

  votes = [ Vote.objects.get(pk = x) for x in votes ] 

  mk_votes = {}
  pty_votes = {}

  for p in Party.objects.all():
    pty_votes[p.pk] = 0

  for m in Member.objects.all():
    mk_votes[m.pk] = 0

  for v in votes:
    p_votes={}
    for m in Member.objects.all():
      va = VoteAction.objects.filter( member = m, vote = v, type__in=['for','against'] )
      if va.count() != 0:
        mk_votes[m.pk] += 1
        if m.current_party != None:
          p_votes.setdefault(m.current_party.pk,0)
          p_votes[m.current_party.pk] += (1 if va[0].type == 'against' else -1)
    for pname, num in p_votes.iteritems():
      pty_votes[pname] += abs(num)

  #print pty_members
  #print pty_votes 
  #print mk_votes

  tp = [tagname.encode("utf8")]

  for p in Party.objects.all():
    pk = p.pk
    inv = 1.0 * pty_votes[pk] / pty_members[pk]
    tp.append("%.3f" % (inv/len(votes), ) )
  print ",".join(tp)
