import os
from django.template import loader, RequestContext
from django.http import Http404, HttpResponse
from django.core.xheaders import populate_xheaders
from django.core.paginator import Paginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import list_detail
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

class ClassBasedView(object):
    def __call__(self, request, **kwargs):
        self.pre(request, **kwargs)       
        ret = self.render(request, **kwargs)
        return self.post(request, ret, **kwargs)

    def pre (self, request, **kwargs):
        pass

    def post(self, request, ret, **kwargs):
        return ret
        
    def full_to_part(self, template_name):
        return os.path.join(os.path.dirname(template_name),
                            "_%s" % os.path.basename(template_name))

class SimpleView(ClassBasedView):
    def __init__(self, template):
        self.template = template

    def render (self,request):
        if 'part' in request.GET:   template_name = self.full_to_part(self.template)
        else:                       template_name = self.template

        return direct_to_template(request, template=template_name)

class ListDetailView(ClassBasedView):
    """
    Generic view of an object or a list of objects

    Templates:
        if ``part`` is given, either as a parameter or as GET data the template
        to be used will be one of:
            - <app_lable>/_object_[list|detail].html
            - <app_label>/_<template_name>
        depending on whether template_name is given.

    Properties:
        include_dir:    where the partial template is
    """

    def __init__(self, queryset, paginate_by = None, extra_context = None):
        self.queryset = queryset
        self.paginate_by = paginate_by
        self.extra_context = extra_context

    def render_list(self, request, queryset=None, page=None,
            allow_empty=True, template_name=None, template_loader=loader,
            extra_context=None, context_processors=None, template_object_name='object',
            mimetype=None):
        """
        if 'part' in request.GET:
            model = self.queryset.model
            if template_name not in kwargs:
                template_name = "%s/%s/_%s_list.html" % (model._meta.app_label,
                                                                include_dir, 
                                                                model._meta.object_name.lower())
            else:
                template_name = "%s/%s/_%s.html" % (model._meta.app_label,
                                                           include_dir,
                                                           kwargs[tempale_name])
            kwargs['template_name'] = template_name

        kwargs['queryset'] = self.queryset
        return list_detail.object_list (request, **kwargs)
        """
        """
        Generic list of objects.

        Templates: ``<app_label>/<model_name>_list.html``
        Context:
            object_list
                list of objects
            is_paginated
                are the results paginated?
            results_per_page
                number of objects per page (if paginated)
            has_next
                is there a next page?
            has_previous
                is there a prev page?
            page
                the current page
            next
                the next page
            previous
                the previous page
            pages
                number of pages, total
            hits
                number of objects, total
            last_on_page
                the result number of the last of object in the
                object_list (1-indexed)
            first_on_page
                the result number of the first object in the
                object_list (1-indexed)
            page_range:
                A list of the page numbers (1-indexed).
        """
        if self.extra_context:
            ec = dict(self.extra_context) 
        else:
            ec = {}
        ec.update(extra_context or {})        
        
        if queryset==None:            
            queryset = self.queryset._clone()
        if self.paginate_by:
            paginator = Paginator(queryset, self.paginate_by, allow_empty_first_page=allow_empty)
            if not page:
                page = request.GET.get('page', 1)
            try:
                page_number = int(page)
            except ValueError:
                if page == 'last':
                    page_number = paginator.num_pages
                else:
                    # Page is not 'last', nor can it be converted to an int.
                    raise Http404
            try:
                page_obj = paginator.page(page_number)
            except InvalidPage:
                raise Http404
            c = RequestContext(request, {
                '%s_list' % template_object_name: page_obj.object_list,
                'paginator': paginator,
                'page_obj': page_obj,

                # Legacy template context stuff. New templates should use page_obj
                # to access this instead.
                'is_paginated': page_obj.has_other_pages(),
                'results_per_page': paginator.per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page': page_obj.number,
                'next': page_obj.next_page_number(),
                'previous': page_obj.previous_page_number(),
                'first_on_page': page_obj.start_index(),
                'last_on_page': page_obj.end_index(),
                'pages': paginator.num_pages,
                'hits': paginator.count,
                'page_range': paginator.page_range,
            }, context_processors)
        else:
            c = RequestContext(request, {
                '%s_list' % template_object_name: queryset,
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
            }, context_processors)
            if not allow_empty and len(queryset) == 0:
                raise Http404
        for key, value in ec.items():
            if callable(value):
                c[key] = value()
            else:
                c[key] = value              
        if not template_name:
            model = queryset.model
            template_name = "%s/%s_list.html" % (model._meta.app_label, model._meta.object_name.lower())
        if 'part' in request.GET:
            template_name = self.full_to_part(template_name)
        t = template_loader.get_template(template_name)
        return HttpResponse(t.render(c), mimetype=mimetype)

    def render_object(self, request, object_id=None, slug=None,
            slug_field='slug', template_name=None, template_name_field=None,
            template_loader=loader, extra_context=None,
            context_processors=None, template_object_name='object',
            mimetype=None, include_dir='include'):
        """
        Generic detail of an object.

        Templates: 
            if full ``<app_label>/<model_name>_detail.html`` or
            ``<app_label>/<include_dir>/_<model_name>_detail.html``

        Context:
            object
                the object
        """
        if self.extra_context:
            ec = dict(self.extra_context) 
        else:
            ec = {}
        ec.update(extra_context or {})     
        model = self.queryset.model

        if object_id:
            queryset = self.queryset.filter(pk=object_id)
        elif slug and slug_field:
            queryset = self.queryset.filter(**{slug_field: slug})
        else:
            raise AttributeError, "Generic detail view must be called with either an object_id or a slug/slug_field."

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404, "No %s found matching the query" % (model._meta.verbose_name)

        if not template_name:
            template_name = "%s/%s_detail.html" % (model._meta.app_label, model._meta.object_name.lower())
        if 'part' in request.GET:
            template_name=self.full_to_part(template_name)
    
        if template_name_field:
            # TODO: if part specified modify the data from template_name_field
            template_name_list = [getattr(obj, template_name_field), template_name]
            t = template_loader.select_template(template_name_list)
        else:
            t = template_loader.get_template(template_name)
        c = RequestContext(request, {
            template_object_name: obj,
        }, context_processors)
        for key, value in ec.items():
            if callable(value):
                c[key] = value()
            else:
                c[key] = value
        response = HttpResponse(t.render(c), mimetype=mimetype)
        populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.name))
        return response

    def render(self, request, **kwargs):
        include_dir = getattr(kwargs, "include_dir", "include")
        if request.method == "POST":
            return self.handle_post(request, **kwargs)
        if 'object_id' in kwargs:
            return self.render_object(request, **kwargs)
        else:
            return self.render_list(request, **kwargs)

