from functools import wraps, update_wrapper
from base import View
from list import ListView
from detail import DetailView
from dates import (ArchiveView, YearView, MonthView,
                                     WeekView, DayView, TodayView,
                                     DateDetailView)
from edit import (FormView, CreateView, UpdateView,
                                    DeleteView)
def method_decorator(decorator):
    """
    Converts a view function decorator into a method decorator.
    the special thing about view decorators is that they expect 
    'request' to be their first argument.
    Example:

        class MyView(View):
            allowed_methods = ['GET','POST'],

            @method_decorator(login_required)
            def POST(*arg, **kwargs):
                ...
    """
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            def bound_func(request, *args2, **kwargs2):
                return func(self, *args2, **kwargs2)
            # bound_func has the signature that 'decorator' expects i.e.  no
            # 'self' argument, but it is a closure over self so it can call
            # 'func' correctly.
            return decorator(bound_func)(self.request, *args, **kwargs)
        return wraps(func)(_wrapper)
    update_wrapper(_dec, decorator)
    # Change the name to aid debugging.
    _dec.__name__ = 'method_dec(%s)' % decorator.__name__
    return _dec

