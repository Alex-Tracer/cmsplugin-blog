from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from cmsplugin_blog.models import LatestEntriesPlugin, Entry, LatestTaggedEntriesPlugin

from tagging.models import TaggedItem
from tagging.utils import get_tag

class CMSLatestEntriesPlugin(CMSPluginBase):
    """
        Plugin class for the latest entries
    """
    model = LatestEntriesPlugin
    name = _('Latest entries')
    render_template = "cmsplugin_blog/latest_entries.html"
    
    def render(self, context, instance, placeholder):
        """
            Render the latest entries
        """
        qs = Entry.published.all()
        
        if instance.current_language_only:
            from cms.utils import get_language_from_request
            language = get_language_from_request(context["request"])
            qs = qs.filter(entrytitle__language=language)
            
        latest = qs[:instance.limit]
        context.update({
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSLatestEntriesPlugin)

class CMSLatestTaggedEntriesPlugin(CMSPluginBase):
    model = LatestTaggedEntriesPlugin
    name = _('Latest tagged entries')
    render_template = "cmsplugin_blog/latest_tagged.html"
    
    def render(self, context, instance, placeholder):
        queryset = Entry.objects.all()
        tag_instance = get_tag(instance.tag)
        queryset = TaggedItem.objects.get_by_model(queryset, tag_instance)
        if instance.limit:
            queryset = queryset[:instance.limit]
        context.update({
            'latest': queryset,
            'tag': instance.tag,
            'display_type': instance.display_type
        })
        if instance.characters_limit:
            context.update({'char_limit': instance.characters_limit})
        
        return context
        
plugin_pool.register_plugin(CMSLatestTaggedEntriesPlugin)