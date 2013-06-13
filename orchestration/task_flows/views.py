from django.views.generic.base import TemplateView

from horizon import exceptions
from horizon import tables

from orchestration.common.tables import WorkflowTable, TableData
from orchestration.common.breadcrumbs import Breadcrumbs

class IndexView(tables.DataTableView):
    table_class = WorkflowTable
    template_name = 'orchestration/workflows/workflows.html'

    def get_data(self):
        request = self.request
        d3 = TableData(id='3',stack_name='Wordpress3',type='taskflows')
        d4 = TableData(id='4',stack_name='Wordpress4',type='taskflows')
        d4.stack_status = 'Create Failed'

        try:
            stacks = [d3, d4]
        except:
            exceptions.handle(request,
                              ('Unable to retrieve stack list.'))
        return stacks


class TaskFlowView(Breadcrumbs):
    template_name = 'orchestration/workflows/task_flow.html'

    def get_context_data(self, **kwargs):
        stack_name = kwargs.get('stack_name','')

        context = super(TaskFlowView, self).get_context_data(**kwargs)
        context['stack_name'] = stack_name
        context['title'] = stack_name + ' Task Flow'
        return context