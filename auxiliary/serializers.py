from django.core.serializers.xml_serializer import Serializer as XmlSerializer
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.functional import Promise


class Serializer(XmlSerializer):
    """Extends XmlSerializer and hides sensitive data. That way we can provide
    consistent and updated db for developers

    Also saves memory by writing to the stream each object, instead of a dump on
    all collected objects

    """

    def start_object(self, obj):
        """Set users password's to unusable values"""

        model_name = smart_unicode(obj._meta)

        if model_name == 'auth.user':
            # set_unusable_password won't save the object, so should be safe
            obj.set_unusable_password()

        super(Serializer, self).start_object(obj)

    def handle_field(self, obj, field):
        """Special case models with sensitive data"""

        model_name = smart_unicode(obj._meta)
        field_name = field.name
        value = field._get_val_from_obj(obj)

        if model_name == u'auth.user' and field_name in \
                ('username', 'email', 'first_name', 'last_name'):
            uid = 'user_%s' % obj.pk
            if field_name == 'email':
                value = '%s@example.com' % uid
            else:
                value = uid
        else:
            if field_name.find('email') > -1:
                value = 'xxx@example.com'

        setattr(obj, field_name, value)
        super(Serializer, self).handle_field(obj, field)


class PromiseAwareJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        return super(PromiseAwareJSONEncoder, self).default(o)
