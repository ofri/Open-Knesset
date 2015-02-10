from django.utils.encoding import smart_text
from django.db.models import Q, Manager, Model
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

class PersonManager(Manager):

    def get_by_name(self, name, create=False):
        name = smart_text(name)
        persons = self.filter((Q(aliases__name__in=name) | Q(name=name)))
        if persons:
            return persons[0]
        else:
            if create:
                return self.create(name=name)
            return None
