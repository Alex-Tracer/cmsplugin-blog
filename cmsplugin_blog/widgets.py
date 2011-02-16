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
        #js = (
            #settings.JQUERY_JS, settings.JQUERY_UI_JS
        #)

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
            if (jQuery) {
              var jq_copy = jQuery.noConflict(true);
            }
            </script>
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.0/jquery.min.js"></script>
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.9/jquery-ui.min.js"></script>
            <script type="text/javascript">
            var ac_jq = jQuery.noConflict(true);
            if (jq_copy) {
              jQuery = jq_copy;
            }
            function comma_split(val) {
              return val.split(/,\s*/);
            }
            function extract_last(term) {
              return comma_split(term).pop();
            }
            function ac_select(event, ui) {
              var terms = comma_split(event.target.value);
              terms.pop();
              terms.push(ui.item.value);
              terms.push('');
              event.target.value = terms.join(', ');
              return false;
            }
            ac_jq("#id_%s").autocomplete({
              source: function(request, response) {
                var term = extract_last(request.term);
                var current = comma_split(request.term);
                list = %s;
                response(ac_jq.grep(list, function(el){ return el.indexOf(term) == 0 && ac_jq.inArray(el, current)}));
              },
              select: ac_select
            });
            </script>''' % (name, tag_list))
