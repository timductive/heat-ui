from datetime import datetime

from .breadcrumbs import Breadcrumbs


class TopologyView(Breadcrumbs):
    template_name = 'heat/common/topology.html'

    def get_context_data(self, **kwargs):
        stack_name = kwargs.get('stack_name','')

        context = super(TopologyView, self).get_context_data(**kwargs)
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Topology Graph'
        return context

class LogView(Breadcrumbs):
    template_name = 'heat/common/logs.html'

    def get_context_data(self, **kwargs):
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")

        context = super(LogView, self).get_context_data(**kwargs)
        stack_name = kwargs.get('stack_name','')
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Logs'

        context['today'] = today

        return context