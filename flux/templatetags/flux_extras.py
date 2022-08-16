from litreview.settings import TIME_ZONE
from django import template
import pytz

register = template.Library()


@register.filter
def model_type(value):
    return type(value).__name__


@register.simple_tag(takes_context=True)
def get_poster_display_verb(
    context,
    user,
):
    if user == context["user"]:
        return " Vous avez"
    return user.username + " a"


@register.simple_tag(takes_context=True)
def get_poster_display(
    context,
    user,
):
    if user == context["user"]:
        return " Vous"
    return user.username


@register.filter
def return_list(n):
    return range(n)


@register.filter
def my_date(date):
    local_tz = pytz.timezone(TIME_ZONE)
    date = date.astimezone(local_tz)
    return date.strftime("à %H:%M le %d %B %Y")
