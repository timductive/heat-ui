import yaml
import json
import collections

from horizon import forms
from django.db import models


class HeatTemplate(object):
    template = None
    json = None
    form = None

    def __init__(self, template):
        # get uploaded form from the cache
        self.template = template
        self.json = yaml.safe_load(template,) #object_pairs_hook=collections.OrderedDict)
        self.form = self.generate_heat_form()

    def generate_heat_form(self):
        '''
        takes a HeatTemplate object
        returns a form object created from the heat template
        '''
        # Collect the fields
        fields = {'stack_name': forms.CharField(
                                   help_text='Unique name for the stack')}
        parameters = self.json.get('Parameters', {})
        for param, val in parameters.items():
            if 'AllowedValues' in val:
                choices = map(lambda x: (x, x), val['AllowedValues'])
                fields[param] = forms.ChoiceField(choices=choices)
            else:
                fields[param] = forms.CharField(
                                    initial=val.get('Default', None),
                                    help_text=val.get('ConstraintDescription',
                                                      ''))
            fields[param].initial = val.get('Default', None)
            fields[param].help_text = val.get('Description', '')
                                       # + val.get('ConstraintDescription', '')
        ####fields['launch_ha'] = forms.BooleanField(required=False)
        # Create the form object
        base_form = type('HeatTemplateBaseForm', (forms.BaseForm,),
                                                 {'base_fields': fields})
        form = type('HeatTemplateForm', (forms.Form, base_form), {})
        # Set the fields order
        # This will have no effect if the params object is not
        # of type collections.OrderedDict
        # use object_pairs_hook=collections.OrderedDict on json.loads
        form.base_fields.keyOrder = parameters.keys()
        form.base_fields.keyOrder.insert(0, 'stack_name')
        ####form.base_fields.keyOrder.append('launch_ha')
        return form

class ContentBase(object):
    def __getattr__(self, key):
        return self.content[key]


class GitContent(ContentBase):
    def __init__(self, content):
        self.id = content['name']
        self.content = content


class AWSContent(ContentBase):
    def __init__(self, content):
        self.id = 'content key not found'
        self.content = {}
        for c in content.getchildren():
            key = c.tag.split('}')[1]
            if key == 'Key':
                key = 'name'
                self.id = c.text
            self.content[key.lower()] = c.text