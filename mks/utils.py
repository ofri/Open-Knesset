import math
from mks.models import Member
from persons.models import Person, PersonAlias

# from: http://www.cs.princeton.edu/introcs/21function/ErrorFunction.java.html
# Implements the Gauss error function.
#   erf(z) = 2 / sqrt(pi) * integral(exp(-t*t), t = 0..z)
#
# fractional error in math formula less than 1.2 * 10 ^ -7.
# although subject to catastrophic cancellation when z in very close to 0
# from Chebyshev fitting formula for erf(z) from Numerical Recipes, 6.2
def erf(z):
    t = 1.0 / (1.0 + 0.5 * abs(z))
    # use Horner's method
    ans = 1 - t * math.exp( -z*z -  1.26551223 +
                                        t * ( 1.00002368 +
                                        t * ( 0.37409196 +
                                        t * ( 0.09678418 +
                                        t * (-0.18628806 +
                                        t * ( 0.27886807 +
                                        t * (-1.13520398 +
                                        t * ( 1.48851587 +
                                        t * (-0.82215223 +
                                        t * ( 0.17087277))))))))))
    if z >= 0.0:
        return ans
    else:
        return -ans


def percentile(avg,var,val):
    if not var:
        return 50
    z = (val-avg)/math.sqrt(var)
    p = erf(z)/2.0*100.0+50.0
    p = int(round(p))
    p = min(100,p)
    p = max(0,p)
    return p


def get_all_mk_names():
    mks = []
    mk_names = []
    current_mks = Member.current_knesset.filter(is_current=True)
    mks.extend(current_mks)
    mk_names.extend(current_mks.values_list('name', flat=True))
    current_mk_ids = [m.id for m in current_mks]
    mk_persons = Person.objects.filter(
        mk__isnull=False,
        mk__id__in=current_mk_ids).select_related('mk')
    mk_aliases = PersonAlias.objects.filter(
        person__in=mk_persons).select_related('person', 'person__mk')
    mks.extend([person.mk for person in mk_persons])
    mk_names.extend(mk_persons.values_list('name', flat=True))
    mks.extend([alias.person.mk for alias in mk_aliases])
    mk_names.extend(mk_aliases.values_list('name', flat=True))
    return (mks, mk_names)
