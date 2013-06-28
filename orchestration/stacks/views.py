# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import httplib2

from horizon import exceptions
from horizon import tables
from horizon import tabs
from horizon import workflows
from horizon import messages

from django.template.defaultfilters import title
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.views import generic

from openstack_dashboard import api

from orchestration.common.breadcrumbs import Breadcrumbs
from orchestration.common.jsonutils import to_json
from .tables import StacksTable
from .tabs import ResourceDetailTabs, StackDetailTabs
from .workflows import LaunchStack
from .models import HeatTemplate


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = StacksTable
    template_name = 'orchestration/stacks/index.html'

    def _inject_name(self, stack):
        # Horizon expects the object to have a name property
        # in order for the delete functionality to work properly
        # this function is mapped onto a stack object
        # setting the name property equal to the stack_name
        stack.name = stack.stack_name
        return stack

    def get_data(self):
        request = self.request
        request.session['heat_template'] = None
        request.session['heat_template_name'] = None
        try:
            stacks = api.heat.stacks_list(self.request)
            stacks = map(self._inject_name, stacks)
            print stacks
        except Exception as e:
            print 'ERROR'
            print e
            # exceptions.handle(request, 'Unable to retrieve stack list.')
        return stacks


class LaunchStackView(workflows.WorkflowView, Breadcrumbs):
    workflow_class = LaunchStack

    def get_initial(self):
        initial = super(LaunchStackView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial

class LaunchHeatView(generic.FormView, Breadcrumbs):
    template_name = 'orchestration/stacks/launch.html'
    success_url = reverse_lazy('horizon:heat:stacks:index')

    def get(self, request, *args, **kw):
        template_url = request.session.get('heat_template_url', None)
        template_name = request.session.get('heat_template_name', None)

        h = httplib2.Http(".cache",disable_ssl_certificate_validation=True)
        resp, template = h.request(template_url, "GET")

        if template is None:
            if 'HTTP_REFERER' in request.META:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse('horizon:heat:stacks:launch'))
        t = HeatTemplate(template)
        context = {'form': t.form(),
                   'template_name': template_name}
        return self.render_to_response(context)

    def post(self, request, *args, **kw):
        template_url = request.session.get('heat_template_url', None)
        template_name = request.session.get('heat_template_name', None)

        h = httplib2.Http(".cache",disable_ssl_certificate_validation=True)
        resp, template = h.request(template_url, "GET")

        if template is None:
            if 'HTTP_REFERER' in request.META:
                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                return HttpResponseRedirect(reverse('horizon:thermal:stacks:upload'))
        t = HeatTemplate(template)
        form = t.form(request.POST)
        if form.is_valid():
            try:
                stack_name = form.cleaned_data.pop('stack_name')
                params = {'stack_name': stack_name,
                          'template': t.json,
                          'parameters': form.cleaned_data,}
                result = api.heat.stack_create(request, **params)
            except Exception, e:
                messages.error(request, e)
                return self.render_to_response({'form': form,
                                                'template_name': template_name})
        else:
            return self.render_to_response({'form': form,
                                                'template_name': template_name})
        return HttpResponseRedirect(self.success_url)

class DetailView(tabs.TabView, Breadcrumbs):
    tab_group_class = StackDetailTabs
    template_name = 'orchestration/stacks/detail.html'

    def get_context_data(self, **kwargs):
        request = self.request
        context = super(DetailView, self).get_context_data(**kwargs)
        context["stack"] = stack = self.get_data(self.request)
        context["title"] = title(stack.stack_name) + ' Overview'
        return context

    def get_data(self, request, **kwargs):
        if not hasattr(self, "_stack"):
            stack_id = kwargs['stack_id']
            try:
                stack = api.heat.stack_get(request, stack_id)
                self._stack = stack
            except Exception as msg:
                msg = str(msg) + "Unable to retrieve stack."
                redirect = reverse('horizon:project:stacks:index')
                exceptions.handle(request, msg, redirect=redirect)
        return self._stack

    def get_tabs(self, request, **kwargs):
        stack = self.get_data(request, **kwargs)
        return self.tab_group_class(request, stack=stack, **kwargs)


class ResourceView(tabs.TabView):
    tab_group_class = ResourceDetailTabs
    template_name = 'orchestration/stacks/resource.html'

    def get_context_data(self, **kwargs):
        context = super(ResourceView, self).get_context_data(**kwargs)
        context["resource"] = self.get_data(self.request, **kwargs)
        context["metadata"] = self.get_metadata(self.request, **kwargs)
        return context

    def get_data(self, request, **kwargs):
        if not hasattr(self, "_resource"):
            try:
                resource = api.heat.resource_get(
                    request,
                    kwargs['stack_id'],
                    kwargs['resource_name'])
                self._resource = resource
            except:
                msg = _("Unable to retrieve resource.")
                redirect = reverse('horizon:project:stacks:index')
                exceptions.handle(request, msg, redirect=redirect)
        return self._resource

    def get_metadata(self, request, **kwargs):
        if not hasattr(self, "_metadata"):
            try:
                metadata = api.heat.resource_metadata_get(
                    request,
                    kwargs['stack_id'],
                    kwargs['resource_name'])
                self._metadata = json.dumps(metadata, indent=2)
            except:
                msg = _("Unable to retrieve metadata.")
                redirect = reverse('horizon:project:stacks:index')
                exceptions.handle(request, msg, redirect=redirect)
        return self._metadata

    def get_tabs(self, request, **kwargs):
        resource = self.get_data(request, **kwargs)
        metadata = self.get_metadata(request, **kwargs)
        return self.tab_group_class(
            request, resource=resource, metadata=metadata, **kwargs)
