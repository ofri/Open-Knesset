from django.db import models
import json
from django.utils.simplejson import JSONEncoder as DjangoJSONEncoder
from datetime import datetime

class JsonField(models.TextField):
    """JsonField is a textfield that contains JSON-serialized dictionaries."""

    #__metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert string value to JSON after loading from the DB."""
        value = json.loads(value)
        return value

    def get_db_prep_save(self, value):
        """Convert JSON object to a string before save."""
        value = json.dumps(value, cls=DjangoJSONEncoder, ensure_ascii=False)
        return super(JsonField, self).get_db_prep_save(value)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^knesset\.annotations\.models\.JsonField"])

class AnnotationPermissions(models.Model):
    read = JsonField(default=[])
    update = JsonField(default=[])
    delete = JsonField(default=[])
    admin = JsonField(default=[])

    def __repr__(self):
      return ("id=" + repr(self.id) +
              ", read=" + repr(self.read) +
              ", update=" + repr(self.update) +
              ", delete=" + repr(self.delete) +
              ", admin=" + repr(self.admin))
    def __str__(self):
      return repr(self)

class Annotation(models.Model):
    annotator_schema_version = models.CharField(max_length=20)
    uri = models.URLField()
    account_id = models.CharField(max_length=255) # Arbitrary limit
    #TODO(shmichael): Add real django user here.
    user = JsonField()
    text = models.TextField()
    quote = models.TextField(default="")
    created = models.DateTimeField(default=datetime.now)
    ranges = JsonField()
    #TODO(shmichael): Add django tags here.
    tags = JsonField()
    permissions = models.ForeignKey(AnnotationPermissions, db_index=True)
