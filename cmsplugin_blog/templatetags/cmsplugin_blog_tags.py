import datetime
from django import template

from tagging.models import Tag

from cms.utils import get_language_from_request
from cmsplugin_blog.models import Entry, EntryTitle
from cms.models import Placeholder

import classytags
import re
from django.utils.encoding import force_unicode
from django.template.defaultfilters import safe

register = template.Library()

@register.inclusion_tag('cmsplugin_blog/month_links_snippet.html', takes_context=True)
def render_month_links(context):
    request = context["request"]
    language = get_language_from_request(request)
    return {
        'dates': Entry.published.filter(entrytitle__language=language).dates('pub_date', 'month'),
    }

@register.inclusion_tag('cmsplugin_blog/tag_links_snippet.html', takes_context=True)
def render_tag_links(context):
    request = context["request"]
    language = get_language_from_request(request)
    filters = dict(is_published=True, pub_date__lte=datetime.datetime.now(), entrytitle__language=language)
    return {
        'tags': Tag.objects.usage_for_model(Entry, filters=filters)
    }
    
@register.filter
def choose_placeholder(placeholders, placeholder):
    try:
        return placeholders.get(slot=placeholder)
    except Placeholder.DoesNotExist:
        return None

class RenderEntry(classytags.core.Tag):
    name = 'render_entry'
    options = classytags.core.Options(
        classytags.arguments.Argument('entry'),
        classytags.arguments.Argument('slot'),
        classytags.arguments.Argument('char_limit', default=None, required=False),
        classytags.arguments.Argument('width', default=None, required=False),
    )
    
    def render_tag(self, context, entry, slot, char_limit, width):
        request = context.get('request', None)
        if not request:
            return ''
        try:
            placeholder = entry.placeholders.get(slot=slot)
        except Placeholder.DoesNotExist:
            return None        
        if not placeholder:
            return ''
        text = placeholder.render(context, width)
        if char_limit:
            text = re.sub(r'<[^>]*?>', ' ', force_unicode(text))
            length = len(text)
            text = text[:char_limit] + ('...' if length > char_limit else '')
        elif hasattr(request, 'placeholder_media'):
            request.placeholder_media += placeholder.get_media(request, context)            
        return safe(text)

register.tag(RenderEntry)
