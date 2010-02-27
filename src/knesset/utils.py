from datetime import datetime
from haystack.forms import SearchForm

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
