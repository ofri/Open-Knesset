from django.core.management.base import  CommandError, NoArgsCommand
from knesset.links.models import Link

class Command(NoArgsCommand):
    help = 'Deactivate duplicated links compared by URL and content object'

    def handle_noargs(self, **options):
        uniqLinks = set()
        numberOfDuplicatedLinks = 0
        for l in Link.objects.all():
            if ((l.url, l.content_object) in  uniqLinks):
#                This link already exists, deactive it
                l.active = False
                l.save()
                numberOfDuplicatedLinks += 1
            else:
                uniqLinks.add((l.url, l.content_object))
        self.stdout.write('Deactivated %d duplicated links\n' % numberOfDuplicatedLinks)