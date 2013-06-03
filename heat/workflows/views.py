from datetime import datetime

from django.utils.safestring import mark_safe

from horizon import exceptions
from horizon import tables

from heat.common.tables import WorkflowTable

class TableData(object):
    id = '1'
    stack_name = 'Wordpress'
    creation_time = str(datetime.now())
    updated_time = str(datetime.now())
    stack_status = 'Create In Progress'
    view = mark_safe(
        "<a href=''>Tasks</a> | "
        "<a href=''>Topology</a> | "
        "<a href=''>Logs</a>")

d1 = TableData()
d2 = TableData()
d2.id = '2'
d2.stack_status = 'Create Failed'
d2.view = mark_safe(
        "<a href=''>Retry</a> | "
        "<a href=''>Tasks</a> | "
        "<a href=''>Topology</a> | "
        "<a href=''>Logs</a>"
)


class IndexView(tables.DataTableView):
    table_class = WorkflowTable
    template_name = 'heat/workflows/workflows.html'

    def get_data(self):
        request = self.request
        try:
            stacks = [d1, d2]
        except:
            exceptions.handle(request,
                              ('Unable to retrieve stack list.'))
        return stacks