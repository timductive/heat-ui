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
import os
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from horizon import messages
from horizon import tabs
from openstack_dashboard import api

from orchestration.common.tables import LogsTable
from orchestration.stacks.api import d3_data
from .tables import EventsTable
from .tables import ResourcesTable

LOG = logging.getLogger(__name__)

class StackTopologyTab(tabs.Tab):
    name = _("Topology")
    slug = "topology"
    template_name = "orchestration/stacks/_overview_topology.html"
    preload = False

    def get_context_data(self, request):
        context = {}
        stack = self.tab_group.kwargs['stack']
        context['stack_id'] = stack.id
        context['d3_data'] = d3_data(request, stack_id=stack.id)
        return context

class StackMetadataTab(tabs.Tab):
    name = _("Metadata")
    slug = "metadata"
    template_name = "orchestration/stacks/_detail_metadata.html"

    def get_context_data(self, request):
        return {"stack": self.tab_group.kwargs['stack']}


class ResourceOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "resource_overview"
    template_name = "orchestration/stacks/_resource_overview.html"

    def get_context_data(self, request):
        return {
            "resource": self.tab_group.kwargs['resource'],
            "metadata": self.tab_group.kwargs['metadata']}


class StackEventsTab(tabs.Tab):
    name = _("Events")
    slug = "events"
    template_name = "orchestration/stacks/_detail_events.html"
    preload = False

    def get_context_data(self, request):
        stack = self.tab_group.kwargs['stack']
        try:
            stack_identifier = '%s/%s' % (stack.stack_name, stack.id)
            events = api.heat.events_list(self.request, stack_identifier)
            LOG.debug('got events %s' % events)
        except:
            events = []
            messages.error(request, _(
                'Unable to get events for stack "%s".') % stack.stack_name)
        return {"stack": stack,
                "table": EventsTable(request, data=events), }

class StackTemplateTab(tabs.Tab):
    name = _("Template")
    slug = "template"
    template_name = "orchestration/stacks/_overview_template.html"

    def get_context_data(self, request):
        return {"stack": self.tab_group.kwargs['stack']}

class Log(object):
    def __init__(self):
        self.id = ''
        self.description = ''

class StackLogsTab(tabs.Tab):
    name = _("Logs")
    slug = "logs"
    template_name = "orchestration/stacks/_overview_logs.html"

    def get_context_data(self, request):
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")

        #Get Log Array for demo
        logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine.log')
        logs = []
        id=0
        previous_time = ''
        previous_type = ''
        log = Log()
        for line in open(logfile, 'r'):
            split = line.split(' ')

            current_time = split[1]
            current_type = split[3]
            current_description = ' '.join(split[5:])

            log.id = str(id)
            log.date = split[0]
            log.time = current_time
            log.nbr = split[2]
            log.type = current_type
            log.location = split[4]
            if log.description:
                log.description+='<br>'+current_description
            else:
                log.description=current_description

            if previous_time != current_time or previous_type != current_type:
                if log.type == 'ERROR':
                    log.description=mark_safe("<span class='error'>"+log.description+"</span>")
                elif log.type == 'DEBUG':
                    log.description=mark_safe("<span class='debug'>"+log.description+"</span>")
                else:
                    log.description=mark_safe(log.description)
                logs.append(log)
                log = Log()
                id+=1
                previous_time = current_time
                previous_type = current_type

        context = {}
        stack = self.tab_group.kwargs['stack']
        stack_name = stack.stack_name
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Logs'
        context['today'] = today
        context['logs'] = LogsTable(request,data=logs)
        return context

class StackResourcesTab(tabs.Tab):
    name = _("Resources")
    slug = "resources"
    template_name = "orchestration/stacks/_detail_resources.html"
    preload = False

    def get_context_data(self, request):
        stack = self.tab_group.kwargs['stack']
        try:
            stack_identifier = '%s/%s' % (stack.stack_name, stack.id)
            resources = api.heat.resources_list(self.request, stack_identifier)
            LOG.debug('got resources %s' % resources)
        except:
            resources = []
            messages.error(request, _(
                'Unable to get resources for stack "%s".') % stack.stack_name)
        return {"stack": stack,
                "table": ResourcesTable(
                    request, data=resources, stack=stack), }


class StackDetailTabs(tabs.TabGroup):
    slug = "stack_details"
    tabs = (StackTopologyTab, StackMetadataTab, StackResourcesTab, StackEventsTab, StackTemplateTab, StackLogsTab)
    sticky = True


class ResourceDetailTabs(tabs.TabGroup):
    slug = "resource_details"
    tabs = (ResourceOverviewTab,)
    sticky = True
