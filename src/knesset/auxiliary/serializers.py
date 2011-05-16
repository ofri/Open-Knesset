from django.core.serializers.json import Serializer as JsonSerializer
from django.utils.encoding import smart_unicode, is_protected_type

class Serializer(JsonSerializer):
    """Extends JsonSerializer and hides sensitive data. That way we can provide
    consistent and updated db for developers

    """
    def start_object(self, obj):
        """Set users password's to unusable values"""

        super(Serializer, self).start_object(obj)

        model_name = smart_unicode(obj._meta)
        if model_name == 'auth.user':
            # set_unusable_password won't save the object, so should be safe
            obj.set_unusable_password()


    def handle_field(self, obj, field):
        """Special case models with sensitive data"""

        model_name = smart_unicode(obj._meta)
        field_name = field.name
        if model_name == u'auth.user' and field_name in \
                ('username', 'email', 'first_name', 'last_name'):
            uid = 'user_%s' % obj.pk
            if field_name == 'email':
               value = '%s@example.com' % uid
            else:
                value = uid

            self._current[field_name] = value
        else:
            value = field._get_val_from_obj(obj)

            # Protected types (i.e., primitives like None, numbers, dates,
            # and Decimals) are passed through as is. All other values are
            # converted to string first.
            if is_protected_type(value):
                self._current[field_name] = value
            else:
                self._current[field_name] = field.value_to_string(obj)
