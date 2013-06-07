from horizon import exceptions
from horizon import tables

from heat.common.tables import DeploymentsTable, TableData

class IndexView(tables.DataTableView):
    table_class = DeploymentsTable
    template_name = 'heat/deployments/index.html'

    def get_data(self):
        request = self.request
        d1 = TableData(id='1',stack_name='Wordpress1')
        d2 = TableData(id='2',stack_name='Wordpress2')
        try:
            stacks = [d1, d2]
        except:
            exceptions.handle(request,
                              ('Unable to retrieve stack list.'))
        return stacks