from datetime import datetime
import json
import httplib2
import xml.etree.ElementTree as ET

from django.views import generic
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from horizon import tables

from orchestration.common.tables import CloneTable, CataloguesTable, TableData

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

class RsContent():
    def __init__(self, content):
        self.id = content.get('id')
        self.name = content.get('name')
        self.url = content.get('url')

class IndexView(generic.TemplateView):
    template_name = 'orchestration/launch_stack/launch_stack.html'

    def get_context_data(self, **kwargs):
        request = self.request

        #Get RS Heat Templates
        h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
        resp, content = h.request('https://raw.github.com/timductive/rs-heat-templates/master/rackspace/templates.json', "GET")
        content = json.loads(content)
        contents = content.get('templates')
        templates = []
        count = 0
        for t in contents:
            templates.append(RsContent(t))
            count+=1

        context = super(IndexView, self).get_context_data(**kwargs)
        context['templates'] = templates
        context['count'] = count

        return context

    def post(self, *args, **kwargs):
        request = self.request
        template_name = request.POST.get('template_name')
        template_url = request.POST.get('template_url')

        h = httplib2.Http(".cache",disable_ssl_certificate_validation=True)
        resp, template = h.request(template_url, "GET")

        # store the template so we can render it next
        request.session['heat_template'] = template
        request.session['heat_template_name'] = template_name

        return HttpResponseRedirect(reverse("horizon:heat:launch_stack:launch"))




# class IndexView(generic.TemplateView):
#     template_name = 'orchestration/launch_stack/launch_stack.html'
#
#     def get_context_data(self, **kwargs):
#         request = self.request
#
#         d1 = TableData(id='1',stack_name='Wordpress1')
#         d2 = TableData(id='2',stack_name='Wordpress2')
#
#         data = [d1, d2]
#         cat_code = request.GET.get('cat_code','')
#         templates = ''
#         if cat_code == 'aws':
#             #Get AWS Templates
#             h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
#             resp, content = h.request('https://s3.amazonaws.com/cloudformation-templates-us-east-1/', "GET")
#             root = ET.fromstring(content)
#             content = root.findall(".//{http://s3.amazonaws.com/doc/2006-03-01/}Contents")
#             templates = map(lambda x: AWSContent(x), content)
#         elif cat_code == 'rs':
#             #Get RS Heat Templates
#             h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
#             resp, content = h.request('https://raw.github.com/timductive/rs-heat-templates/master/rackspace/templates.json', "GET")
#             content = json.loads(content)
#             contents = content.get('templates')
#             templates = []
#             for t in contents:
#                 templates.append(RsContent(t))
#
#         context = super(IndexView, self).get_context_data(**kwargs)
#
#         context['clone_table'] = CloneTable(request, data=data)
#
#         print 'Before Catalog render'
#         context['catalogue_table'] = CataloguesTable(request, data=templates)
#         context['cat_code'] = cat_code
#
#         return context

# class IndexView(tables.DataTableView):
#     table_class = CataloguesTable
#     template_name = 'orchestration/launch_stack/launch_stack.html'
#
#     def get_data(self):
#         request = self.request
#
#         print request.session.get('template')
#         print request.session.get('template_name')
#
#         #Get RS Heat Templates
#         h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
#         resp, content = h.request('https://raw.github.com/timductive/rs-heat-templates/master/rackspace/templates.json', "GET")
#         content = json.loads(content)
#         contents = content.get('templates')
#         templates = []
#         for t in contents:
#             templates.append(RsContent(t))
#
#         return templates
#
#     def post(self, request):
#         print 'POST!'
#
#         context = {}
#         context['post'] = request.POST
#
#         return render_to_response('orchestration/launch_stack/test.html', context)#HttpResponseRedirect(reverse("horizon:heat:launch_stack:launch"))