from base import View
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404
import re

class DetailView(View):
    """
    Render a "detail" view of an object.

    By default this is a model instance lookedup from `self.queryset`, but the
    view will support display of *any* object by overriding `get_object()`.
    """
    
    def __init__(self, **kwargs):
        self._load_config_values(kwargs, 
            queryset = None,
            slug_field = 'slug',
            template_resource_name = 'object',
            template_name_field = None,
        )
        super(DetailView, self).__init__(**kwargs)
    
    def get_resource(self):
        """
        Get the resource this request wraps. By default this requires
        `self.queryset` and a `pk` or `slug` argument in the URLconf, but
        subclasses can override this to return any object.
        """
        obj = self.get_object()
        return {self.template_resource_name: obj}
    
    def get_object(self):
        """
        FIXME: Does separating this out from get_resource suck?
        This might suck.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        queryset = self.get_queryset()

        # Next, try looking up by primary key.
        object_id = getattr(self, 'object_id', None)
        slug = getattr(self, 'slug', None)
        if object_id:
            queryset = queryset.filter(pk=object_id)
        # Next, try looking up by slug.
        elif slug:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError("Generic detail view %s must be called with "\
                                 "either an object id or a slug." \
                                 % self.__class__.__name__)

        try:
            # FIXME: This is horrible, but is needed for get_template_names
            # What concerns me about this method of passing data around, is
            # any change in the order of the methods being called in 
            # superclasses may break it.
            self.obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404("No %s found matching the query" % \
                          (queryset.model._meta.verbose_name))
        return self.obj
    
    def get_queryset(self):
        """
        Get the queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        if self.queryset is None:
            raise ImproperlyConfigured("%(cls)s is missing a queryset. Define "\
                                       "%(cls)s.queryset, or override "\
                                       "%(cls)s.get_object()." % {
                                            'cls': self.__class__.__name__
                                        })
        return self.queryset._clone()

    def get_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.slug_field

    def get_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        names = super(DetailView, self).get_template_names()

        # If self.template_name_field is set, grab the value of the field
        # of that name from the object; this is the most specific template
        # name, if given.
        if self.template_name_field:
            name = getattr(obj, self.template_name_field, None)
            if name:
                names.insert(0, name)

        # The least-specific option is the default <app>/<model>_detail.html;
        # only use this if the object in question is a model.
        if hasattr(self, 'obj') and hasattr(self.obj, '_meta'):
            names.append("%s/%s_detail.html" % (
                self.obj._meta.app_label,
                self.obj._meta.object_name.lower()
            ))

        return names
