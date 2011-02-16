from django import forms
from django.conf import settings
from django.utils import simplejson
from django.utils.safestring import mark_safe
from tagging.models import Tag
from cmsplugin_blog.models import Entry

class AutoCompleteTagInput(forms.TextInput):
    class Media:
        css = {
            'all': (settings.JQUERY_UI_CSS,)
        }
        js = (
            'js/move_jquery.js',
            settings.JQUERY_JS,
            settings.JQUERY_UI_JS,
            'js/init_jquery.js'
        )

    def render(self, name, value, attrs=None):
        output = super(AutoCompleteTagInput, self).render(name, value, attrs)
        page_tags = Tag.objects.usage_for_model(Entry)
        tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                    ensure_ascii=False)
        return output + mark_safe(u'''
            <style type="text/css">
            .ui-autocomplete li {
              list-style-type: none;
            }
            </style>
            <script type="text/javascript">
            autocomplete_jq("#id_%s").autocomplete({
              source: function(request, response) {
                var term = request.term.split(/,\s*/).pop();
                var current = request.term.split(/,\s*/);
                list = %s;
                response(autocomplete_jq.grep(list, function(el){
                  return el.indexOf(term) == 0 && autocomplete_jq.inArray(el, current);
                }));
              },
              select: function(event, ui) {
                var terms = event.target.value.split(/,\s*/);
                terms.pop();
                terms.push(ui.item.value);
                terms.push('');
                event.target.value = terms.join(', ');
                return false;
              }
            });
            </script>''' % (name, tag_list))
