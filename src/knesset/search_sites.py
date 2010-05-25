import haystack
from haystack.forms import SearchForm

class SearchFormWithSpellSuggest(SearchForm):
    def search(self):
        sqs = super(SearchFormWithSpellSuggest, self).search()
        self.spl = sqs.spelling_suggestion()
        return sqs

haystack.autodiscover()
