from datetime import datetime
import re
from haystack.forms import SearchForm
from django.db import models
from django.contrib.comments.views.comments import post_comment
from django.http import HttpResponse

def limit_by_request(qs, request):
    if 'num' in request.GET:
        num = int(request.GET['num'])
        page = 'page' in request.GET and int(request.GET['page']) or 0
        return qs[page*num:(page+1)*num]
    return qs

def yearstart(year):
    return datetime(year,1,1)

def yearend(year):
    return datetime(year,12,31)

class SearchFormWithSpellSuggest(SearchForm):
    def search(self):
        sqs = super(SearchFormWithSpellSuggest, self).search()
        self.spl = sqs.spelling_suggestion()
        return sqs


def comment_post_wrapper(request):
    # Clean the request to prevent form spoofing
    if request.user.is_authenticated():
        if (('name' in request.POST and (request.user.get_full_name() != request.POST['name'])) or \
                ('email' in request.POST and (request.user.email == request.POST['email']))):
            return HttpResponse("Access denied")
        return post_comment(request)
    return HttpResponse("Access denied")

def cannonize(s):
       if isinstance(s,unicode):
           s = s.replace(u'\u201d','').replace(u'\u2013','')
       else:
           s = s.replace('\xe2\x80\x9d','').replace('\xe2\x80\x93','')
       return re.sub(r'["\(\) ,-\xa0]', '', s)

