from datetime import datetime

from django.utils.safestring import mark_safe

from horizon import exceptions
from horizon import tables

from heat.common.tables import DeploymentsTable

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

class IndexView(tables.DataTableView):
    table_class = DeploymentsTable
    template_name = 'heat/deployments/index.html'

    def get_data(self):
        request = self.request
        try:
            stacks = [d1, d2]
        except:
            exceptions.handle(request,
                              ('Unable to retrieve stack list.'))
        return stacks