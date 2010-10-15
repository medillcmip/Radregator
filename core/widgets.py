import django.forms.widgets
from django import forms
from itertools import chain
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.forms.util import flatatt


from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput

class CheckboxSelectMultipleWithLabelAttrs(CheckboxSelectMultiple):
    """A subclass of CheckboxSelectMultiple to allow 
    def __init__(self, attrs=None, choices=(), label_attrs=None):
        super(CheckboxSelectMultipleWithLabelAttrs, self).__init__(attrs, choices)
        
        # We want to apply attributes (e.g. class) to the label
        self.label_attrs = label_attrs

    def render(self, name, value, attrs=None, choices=(), label_attrs=None):
        # Sadly have to duplicate a lot of this code since it's order-based
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            if self.label_attrs:
                label_attrs_str = flatatt(self.label_attrs)
                
            
            else:
                label_attrs_str = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s%s>%s %s</label></li>' % (label_for, label_attrs_str, rendered_cb, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))



