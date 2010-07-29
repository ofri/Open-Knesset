import time
import datetime
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from list import ListView
from detail import DetailView

class DateView(ListView):
    """
    Abstract base class for date-based views.
    """
    def __init__(self, **kwargs):
        self._load_config_values(kwargs,
            allow_future = False,
            date_field = None,
        )
        super(DateView, self).__init__(**kwargs)

        # Never use legacy pagination context since previous date-based
        # views weren't paginated.
        self.legacy_context = False

    def get(self, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        date_list, items, extra_context = self.get_dated_items(*args, **kwargs)
        template = self.get_template(items)
        context = self.get_context(items, date_list, extra_context)
        mimetype = self.get_mimetype(items)
        response = self.get_response(items, template, context, mimetype=mimetype)
        return response

    def get_queryset(self):
        """
        Get the queryset to look an objects up against. May not be called if
        `get_dated_items` is overridden.
        """
        if self.queryset is None:
            raise ImproperlyConfigured("%(cls)s is missing a queryset. Define "\
                                       "%(cls)s.queryset, or override "\
                                       "%(cls)s.get_dated_items()." \
                                       % {'cls': self.__class__.__name__})
        return self.queryset._clone()

    def get_dated_queryset(self, allow_future=False, **lookup):
        """
        Get a queryset properly filtered according to `allow_future` and any
        extra lookup kwargs.
        """
        qs = self.get_queryset().filter(**lookup)
        date_field = self.get_date_field()
        allow_future = allow_future or self.get_allow_future()
        allow_empty = self.get_allow_empty()

        if not allow_future:
            qs = qs.filter(**{'%s__lte' % date_field: datetime.datetime.now()})

        if not allow_empty and not qs:
            raise Http404("No %s available" % qs.model._meta.verbose_name_plural)

        return qs

    def get_date_list(self, queryset, date_type):
        """
        Get a date list by calling `queryset.dates()`, checking along the way
        for empty lists that aren't allowed.
        """
        date_field = self.get_date_field()
        allow_empty = self.get_allow_empty()

        date_list = queryset.dates(date_field, date_type)[::-1]
        if date_list is not None and not date_list and not allow_empty:
            raise Http404("No %s available" % queryset.model._meta.verbose_name_plural)

        return date_list

    def get_date_field(self):
        """
        Get the name of the date field to be used to filter by.
        """
        if self.date_field is None:
            raise ImproperlyConfigured("%s.date_field is required." % self.__class__.__name__)
        return self.date_field

    def get_allow_future(self):
        """
        Returns `True` if the view should be allowed to display objects from
        the future.
        """
        return self.allow_future

    def get_context(self, items, date_list, context=None):
        """
        Get the context. Must return a Context (or subclass) instance.
        """
        if not context:
            context = {}
        context['date_list'] = date_list
        return super(DateView, self).get_context(
            items, paginator=None, page=None, context=context,
        )

    def get_template_names(self, items):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        return super(DateView, self).get_template_names(items, suffix=self._template_name_suffix)

    def get_dated_items(self, *args, **kwargs):
        """
        Return (date_list, items, extra_context) for this request.
        """
        raise NotImplementedError()

class ArchiveView(DateView):
    """
    Top-level archive of date-based items.
    """

    _template_name_suffix = 'archive'

    def __init__(self, **kwargs):
        self._load_config_values(kwargs, num_latest=15)
        super(ArchiveView, self).__init__(**kwargs)

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        qs = self.get_dated_queryset()
        date_list = self.get_date_list(qs, 'year')
        num_latest = self.get_num_latest()

        if date_list and num_latest:
            latest = qs.order_by('-'+self.get_date_field())[:num_latest]
        else:
            latest = None

        return (date_list, latest, {})

    def get_num_latest(self):
        """
        Get the number of latest items to show on the archive page.
        """
        return self.num_latest

    def get_template_object_name(self, items):
        """
        Get the name of the item to be used in the context.
        """
        return self.template_object_name or 'latest'

class YearView(DateView):
    """
    List of objects published in a given year.
    """

    _template_name_suffix = 'archive_year'

    def __init__(self, **kwargs):
        # Override the allow_empty default from ListView
        allow_empty = kwargs.pop('allow_empty', getattr(self, 'allow_empty', False))
        self._load_config_values(kwargs, make_object_list=False)
        super(YearView, self).__init__(allow_empty=allow_empty, **kwargs)

    def get_dated_items(self, year):
        """
        Return (date_list, items, extra_context) for this request.
        """
        # Yes, no error checking: the URLpattern ought to validate this; it's
        # an error if it doesn't.
        year = int(year)
        date_field = self.get_date_field()
        qs = self.get_dated_queryset(**{date_field+'__year': year})
        date_list = self.get_date_list(qs, 'month')

        if self.get_make_object_list():
            object_list = qs.order_by('-'+date_field)
        else:
            # We need this to be a queryset since parent classes introspect it
            # to find information about the model.
            object_list = qs.none()

        return (date_list, object_list, {'year': year})

    def get_make_object_list(self):
        """
        Return `True` if this view should contain the full list of objects in
        the given year.
        """
        return self.make_object_list

class MonthView(DateView):
    """
    List of objects published in a given year.
    """

    _template_name_suffix = 'archive_month'

    def __init__(self, **kwargs):
        # Override the allow_empty default from ListView
        allow_empty = kwargs.pop('allow_empty', getattr(self, 'allow_empty', False))
        self._load_config_values(kwargs, month_format='%b')
        super(MonthView, self).__init__(allow_empty=allow_empty, **kwargs)

    def get_dated_items(self, year, month):
        """
        Return (date_list, items, extra_context) for this request.
        """
        date_field = self.get_date_field()
        date = _date_from_string(year, '%Y', month, self.get_month_format())

        # Construct a date-range lookup.
        first_day, last_day = _month_bounds(date)
        lookup_kwargs = {
            '%s__gte' % date_field: first_day,
            '%s__lt' % date_field: last_day,
        }

        allow_future = self.get_allow_future()
        qs = self.get_dated_queryset(allow_future=allow_future, **lookup_kwargs)
        date_list = self.get_date_list(qs, 'day')

        return (date_list, qs, {
            'month': date,
            'next_month': self.get_next_month(date),
            'previous_month': self.get_previous_month(date),
        })

    def get_next_month(self, date):
        """
        Get the next valid month.
        """
        first_day, last_day = _month_bounds(date)
        next = (last_day + datetime.timedelta(days=1)).replace(day=1)
        return _get_next_prev_month(self, next, is_previous=False, use_first_day=True)

    def get_previous_month(self, date):
        """
        Get the previous valid month.
        """
        first_day, last_day = _month_bounds(date)
        prev = (first_day - datetime.timedelta(days=1)).replace(day=1)
        return _get_next_prev_month(self, prev, is_previous=True, use_first_day=True)

    def get_month_format(self):
        """
        Get a month format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.month_format

class WeekView(DateView):
    """
    List of objects published in a given week.
    """

    _template_name_suffix = 'archive_year'

    def __init__(self, **kwargs):
        # Override the allow_empty default from ListView
        allow_empty = kwargs.pop('allow_empty', getattr(self, 'allow_empty', False))
        super(WeekView, self).__init__(allow_empty=allow_empty, **kwargs)

    def get_dated_items(self, year, week):
        """
        Return (date_list, items, extra_context) for this request.
        """
        date_field = self.get_date_field()
        date = _date_from_string(year, '%Y', '0', '%w', week, '%U')

        # Construct a date-range lookup.
        first_day = date
        last_day = date + datetime.timedelta(days=7)
        lookup_kwargs = {
            '%s__gte' % date_field: first_day,
            '%s__lt' % date_field: last_day,
        }

        allow_future = self.get_allow_future()
        qs = self.get_dated_queryset(allow_future=allow_future, **lookup_kwargs)

        return (None, qs, {'week': date})

class DayView(DateView):
    """
    List of objects published on a given day.
    """

    _template_name_suffix = "archive_day"

    def __init__(self, **kwargs):
        # Override the allow_empty default from ListView
        allow_empty = kwargs.pop('allow_empty', getattr(self, 'allow_empty', False))
        self._load_config_values(kwargs, month_format='%b', day_format='%d')
        super(DayView, self).__init__(allow_empty=allow_empty, **kwargs)

    def get_dated_items(self, year, month, day, date=None):
        """
        Return (date_list, items, extra_context) for this request.
        """
        date = _date_from_string(year, '%Y',
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        return self._get_dated_items(date)

    def _get_dated_items(self, date):
        """
        Do the actual heavy lifting of getting the dated items; this accepts a
        date object so that TodayView can be trivial.
        """
        date_field = self.get_date_field()
        allow_future = self.get_allow_future()

        field = self.get_queryset().model._meta.get_field(date_field)
        lookup_kwargs = _date_lookup_for_field(field, date)

        qs = self.get_dated_queryset(allow_future=allow_future, **lookup_kwargs)

        return (None, qs, {
            'day': date,
            'previous_day': self.get_previous_day(date),
            'next_day': self.get_next_day(date)
        })

    def get_next_day(self, date):
        """
        Get the next valid day.
        """
        next = date + datetime.timedelta(days=1)
        return _get_next_prev_month(self, next, is_previous=False, use_first_day=False)

    def get_previous_day(self, date):
        """
        Get the previous valid day.
        """
        prev = date - datetime.timedelta(days=1)
        return _get_next_prev_month(self, prev, is_previous=True, use_first_day=False)

    def get_month_format(self):
        """
        Get a month format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.month_format

    def get_day_format(self):
        """
        Get a month format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.day_format

class TodayView(DayView):
    """
    List of objects published today.
    """

    def get_dated_items(self):
        """
        Return (date_list, items, extra_context) for this request.
        """
        return self._get_dated_items(datetime.date.today())

class DateDetailView(DetailView):
    """
    Detail view of a single object on a single date; this differs from the
    standard DetailView by accepting a year/month/day in the URL.
    """
    def __init__(self, **kwargs):
        self._load_config_values(kwargs,
            date_field = None,
            month_format = '%b',
            day_format = '%d',
            allow_future = False,
        )
        super(DateDetailView, self).__init__(**kwargs)

    def get_object(self, year, month, day, pk=None, slug=None, object_id=None):
        """
        Get the object this request displays.
        """
        date = _date_from_string(year, '%Y',
                                 month, self.get_month_format(),
                                 day, self.get_day_format())

        qs = self.get_queryset()

        if not self.get_allow_future() and date > datetime.date.today():
            raise Http404("Future %s not available because %s.allow_future is False." \
                          % (qs.model._meta.verbose_name_plural, self.__class__.__name__))

        # Filter down a queryset from self.queryset using the date from the
        # URL. This'll get passed as the queryset to DetailView.get_object,
        # which'll handle the 404
        date_field = self.get_date_field()
        field = qs.model._meta.get_field(date_field)
        lookup = _date_lookup_for_field(field, date)
        qs = qs.filter(**lookup)

        return super(DateDetailView, self).get_object(queryset=qs,
                              pk=pk, slug=slug, object_id=object_id)

    def get_date_field(self):
        """
        Get the name of the date field to be used to filter by.
        """
        if self.date_field is None:
            raise ImproperlyConfigured("%s.date_field is required." % self.__class__.__name__)
        return self.date_field

    def get_month_format(self):
        """
        Get a month format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.month_format

    def get_day_format(self):
        """
        Get a day format string in strptime syntax to be used to parse the
        month from url variables.
        """
        return self.day_format

    def get_allow_future(self):
        """
        Returns `True` if the view should be allowed to display objects from
        the future.
        """
        return self.allow_future

def _date_from_string(year, year_format, month, month_format, day='', day_format='', delim='__'):
    """
    Helper: get a datetime.date object given a format string and a year,
    month, and possibly day; raise a 404 for an invalid date.
    """
    format = delim.join((year_format, month_format, day_format))
    datestr = delim.join((year, month, day))
    try:
        return datetime.date(*time.strptime(datestr, format)[:3])
    except ValueError:
        raise Http404("Invalid date string '%s' given format '%s'" % (datestr, format))

def _month_bounds(date):
    """
    Helper: return the first and last days of the month for the given date.
    """
    first_day = date.replace(day=1)
    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1)

    return first_day, last_day

def _get_next_prev_month(generic_view, naive_result, is_previous, use_first_day):
    """
    Helper: Get the next or the previous valid date. The idea is to allow
    links on month/day views to never be 404s by never providing a date
    that'll be invalid for the given view.

    This is a bit complicated since it handles both next and previous months
    and days (for MonthView and DayView); hence the coupling to generic_view.

    However in essance the logic comes down to:

        * If allow_empty and allow_future are both true, this is easy: just
          return the naive result (just the next/previous day or month,
          reguardless of object existence.)

        * If allow_empty is true, allow_future is false, and the naive month
          isn't in the future, then return it; otherwise return None.

        * If allow_empty is false and allow_future is true, return the next
          date *that contains a valid object*, even if it's in the future. If
          there are no next objects, return None.

        * If allow_empty is false and allow_future is false, return the next
          date that contains a valid object. If that date is in the future, or
          if there are no next objects, return None.

    """
    date_field = generic_view.get_date_field()
    allow_empty = generic_view.get_allow_empty()
    allow_future = generic_view.get_allow_future()

    # If allow_empty is True the naive value will be valid
    if allow_empty:
        result = naive_result

    # Otherwise, we'll need to go to the database to look for an object
    # whose date_field is at least (greater than/less than) the given
    # naive result
    else:
        # Construct a lookup and an ordering depending on weather we're doing
        # a previous date or a next date lookup.
        if is_previous:
            lookup = {'%s__lte' % date_field: naive_result}
            ordering = '-%s' % date_field
        else:
            lookup = {'%s__gte' % date_field: naive_result}
            ordering = date_field

        qs = generic_view.get_queryset().filter(**lookup).order_by(ordering)

        # Snag the first object from the queryset; if it doesn't exist that
        # means there's no next/previous link available.
        try:
            result = getattr(qs[0], date_field)
        except IndexError:
            result = None

    # Convert datetimes to a dates
    if hasattr(result, 'date'):
        result = result.date()

    # For month views, we always want to have a date that's the first of the
    # month for consistancy's sake.
    if result and use_first_day:
        result = result.replace(day=1)

    # Check against future dates.
    if result and (allow_future or result < datetime.date.today()):
        return result
    else:
        return None

def _date_lookup_for_field(field, date):
    """
    Get the lookup kwargs for looking up a date against a given Field. If the
    date field is a DateTimeField, we can't just do filter(df=date) because
    that doesn't take the time into account. So we need to make a range lookup
    in those cases.
    """
    if isinstance(field, models.DateTimeField):
        date_range = (
            datetime.datetime.combine(date, datetime.time.min),
            datetime.datetime.combine(date, datetime.time.max)
        )
        return {'%s__range' % field.name: date_range}
    else:
        return {field.name: date}

