from django.utils.encoding import smart_text
from django.db.models import Q, Manager, Model
from django.core.exceptions import MultipleObjectsReturned

class PersonManager(Manager):

    def get_by_name(self, name):
        name = smart_text(name)
        try:
            return self.get((Q(aliases__name__in=name) | Q(name=name)))
        except MultipleObjectsReturned:
            ''' just take the first one '''
            return self.filter((Q(aliases__name__in=name) | Q(name=name)))[0]

