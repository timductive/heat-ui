import os
from datetime import datetime

from django.utils.safestring import mark_safe

from orchestration.common.tables import LogsTable
from .breadcrumbs import Breadcrumbs


class TopologyView(Breadcrumbs):
    template_name = 'orchestration/common/topology.html'

    def get_context_data(self, **kwargs):
        stack_name = kwargs.get('stack_name','')

        context = super(TopologyView, self).get_context_data(**kwargs)
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Topology Graph'
        return context

class Log(object):
    def __init__(self):
        self.id = ''
        self.description = ''

class LogView(Breadcrumbs):
    template_name = 'orchestration/common/logs.html'

    def get_context_data(self, **kwargs):
        request = self.request
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

        context = super(LogView, self).get_context_data(**kwargs)
        stack_name = kwargs.get('stack_name','')
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Logs'
        context['today'] = today
        context['logs'] = LogsTable(request,data=logs)
        return context