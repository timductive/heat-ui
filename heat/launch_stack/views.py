from datetime import datetime

from django.views import generic
from django.utils.safestring import mark_safe

from heat.common.tables import CloneTable

class TableData(object):
    id = '1'
    stack_name = 'Wordpress'
    creation_time = str(datetime.now())
    updated_time = str(datetime.now())
    stack_status = 'Create Complete'
    view = mark_safe("<a href=''>Topology</a> | "
                              "<a href=''>Logs</a>")

d1 = TableData()
d2 = TableData()
d2.id = '2'
d2.stack_status = 'Create in Progress'
d2.view = mark_safe(
        "<a href=''>Topology</a> | "
        "<a href=''>Workflow</a> | "
        "<a href=''>Logs</a>"
    )


class IndexView(generic.TemplateView):
    template_name = 'heat/launch_stack/launch_stack.html'

    def get_context_data(self, **kwargs):
        request = self.request
        data = [d1, d2]

        context = super(IndexView, self).get_context_data(**kwargs)

        context['clone_table'] = CloneTable(request, data=data)

        return context
