from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.encoding import smart_str
from base import View

class ListView(View):
    """
    Render some list of objects. This list may be any type via setting
    `self.items`, but if it's a queryset set on `self.queryset` then the
    queryset will be handled correctly.
    """
    def __init__(self, **kwargs):
        self._load_config_values(kwargs, 
            paginate_by = None,
            allow_empty = True,
            template_object_name = None,
           queryset = None,
            itemsset = None,
        )
        super(ListView, self).__init__(**kwargs)

    def GET(self, *args, **kwargs):
        self.page = kwargs.get('page', None)
        self.items = self.get_items()
        paginator, page, self.items = self.paginate_items()
        return super(ListView, self).GET(paginator, page)

    def get_items(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        queryset = self.get_queryset() 
        if queryset:
            return queryset
        if self.itemsset is not None:
            return self.itemsset

        raise ImproperlyConfigured("'%s' must define 'queryset' or 'items'"
                                        % self.__class__.__name__)

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset._clone()
        else:
            return None

    def get_paginate_by(self):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def paginate_items(self):
        """
        Paginate the list of self.items, if needed.
        """
        paginate_by = self.get_paginate_by()
        allow_empty = self.get_allow_empty()
        if not paginate_by:
            if not allow_empty and len(self.items) == 0:
                raise Http404("Empty list and '%s.allow_empty' is False." % self.__class__.__name__)
            return (None, None, self.items)

        paginator = Paginator(self.items, paginate_by, allow_empty_first_page=allow_empty)
        page = self.page or self.request.GET.get('page', 1)
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404("Page is not 'last', nor can it be converted to an int.")
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list)
        except InvalidPage:
            raise Http404('Invalid page (%s)' % page_number)

    def get_template_names(self, suffix='list'):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        import pdb ; pdb.set_trace()
        names = super(ListView, self).get_template_names()

        # If the list is a queryset, we'll invent a template name based on the
        # app and model name. This name gets put at the end of the template
        # name list so that user-supplied names override the automatically-
        # generated ones.
        if hasattr(self.queryset, 'model'):
            opts = self.queryset.model._meta
            names.append("%s/%s_%s.html" % (opts.app_label, opts.object_name.lower(), suffix))

        return names

    def get_context(self, paginator, page, context=None):
        """
        Get the context for this view.
        """
        if not context:
            context = {}
        context.update({
            'paginator': paginator,
            'object_list': self.items,
            'page_obj': page,
            'is_paginated':  paginator is not None
        })
        context = super(ListView, self).get_context(context)
        template_obj_name = self.get_template_object_name()
        context[template_obj_name or 'object_list'] = self.items
        return context

    def get_template_object_name(self):
        """
        Get the name of the item to be used in the context.
        """
        if self.template_object_name:
            return "%s_list" % self.template_object_name
        elif hasattr(self.items, 'model'):
            return smart_str(items.model._meta.verbose_name_plural)
        else:
            return None
    
