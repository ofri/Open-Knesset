from django.db import models
import json
from django.utils.simplejson import JSONEncoder as DjangoJSONEncoder
from datetime import datetime

class DictField(models.TextField):
    """DictField is a textfield that contains JSON-serialized dictionaries."""

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert string value to JSON after loading from the DB."""
        value = json.loads(value)
        assert isinstance(value, dict)
        return value

    def get_db_prep_save(self, value):
        """Convert JSON object to a string before save."""
        assert isinstance(value, dict)
        value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(DictField, self).get_db_prep_save(value)

class CommaDelimitedStringListField(models.TextField):
    """CommaDelimitedStringListField is a textfield that contains a list of strings
       delimited by commas."""
    
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert the string value to a list after loading from the DB."""
        value = value.split(",")
        assert isinstance(value, list)
        return value

    def get_db_prep_save(self, value):
        """Convert the list to a comma-delimited string."""
        assert isinstance(value, list)
        value = ','.join(value)
        return super(CommaDelimitedStringListField, self).get_db_prep_save(value)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^knesset\.annotations\.models\.DictField"])
add_introspection_rules([], ["^knesset\.annotations\.models\.CommaDelimitedStringListField"])

class AnnotationPermissions(models.Model):
    read = CommaDelimitedStringListField(default=[])
    update = CommaDelimitedStringListField(default=[])
    delete = CommaDelimitedStringListField(default=[])
    admin = CommaDelimitedStringListField(default=[])

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
    user = DictField(default={})
    text = models.TextField()
    quote = models.TextField(default="")
    created = models.DateTimeField(default=datetime.now)
    ranges = CommaDelimitedStringListField(default=[])
    #TODO(shmichael): Add django tags here.
    tags = CommaDelimitedStringListField(default=[])
    permissions = models.ForeignKey(AnnotationPermissions, db_index=True)
