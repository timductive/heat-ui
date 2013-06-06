from datetime import datetime
import httplib2
import xml.etree.ElementTree as ET

from django.views import generic
from django.utils.safestring import mark_safe

from heat.common.tables import CloneTable, CataloguesTable

class TableData(object):
    id = '1'
    stack_name = 'Wordpress1'
    creation_time = str(datetime.now())
    updated_time = str(datetime.now())
    stack_status = 'Create Complete'
    view = mark_safe("<a href=''>Topology</a> | "
                              "<a href=''>Logs</a>")

d1 = TableData()
d2 = TableData()
d2.id = '2'
d2.stack_name = 'Wordpress2'

class ContentBase(object):
    def __getattr__(self, key):
        return self.content[key]

class AWSContent(ContentBase):
    def __init__(self, content):
        self.id = 'content key not found'
        self.content = {}
        self.content['view'] = mark_safe("<a href=''>Topology</a>")
        for c in content.getchildren():
            key = c.tag.split('}')[1]
            if key == 'Key':
                key = 'name'
                self.id = c.text
            self.content[key.lower()] = c.text

class IndexView(generic.TemplateView):
    template_name = 'heat/launch_stack/launch_stack.html'

    def get_context_data(self, **kwargs):
        request = self.request
        data = [d1, d2]
        cat_code = request.GET.get('cat_code','')
        templates = ''
        if cat_code == 'aws':
            #Get AWS Templates
            h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
            resp, content = h.request('https://s3.amazonaws.com/cloudformation-templates-us-east-1/', "GET")
            root = ET.fromstring(content)
            content = root.findall(".//{http://s3.amazonaws.com/doc/2006-03-01/}Contents")
            templates = map(lambda x: AWSContent(x), content)

        context = super(IndexView, self).get_context_data(**kwargs)

        context['clone_table'] = CloneTable(request, data=data)
        context['catalogue_table'] = CataloguesTable(request, data=templates)
        context['cat_code'] = cat_code

        return context
