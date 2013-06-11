from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import title, timesince
from django.utils.safestring import mark_safe

from horizon import tables
from horizon.utils.filters import replace_underscores, parse_isotime

class TableData(object):
    def __init__(self, id='', stack_name='', type='stacks', *args, **kwargs):
        self.id = id
        self.stack_name = stack_name
        self.creation_time = str(datetime.now())
        self.updated_time = str(datetime.now())
        if type == 'taskflows':
            self.stack_status = 'Create In Progress'
            self.view = mark_safe(
                                "<a href='task_flow/"+stack_name+"/'>Task Flow</a> | "
                                "<a href='topology/"+stack_name+"/'>Topology</a> | "
                                "<a href='logs/"+stack_name+"/'>Logs</a>")
        else:
            self.stack_status = 'Create Complete'
            self.view = mark_safe("<a href='topology/"+stack_name+"/'>Topology</a> | "
                                      "<a href='logs/"+stack_name+"/'>Logs</a>")




class DeleteStack(tables.BatchAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of")
    data_type_singular = _("Stack")
    data_type_plural = _("Stacks")
    classes = ('btn-danger', 'btn-terminate')

    def allowed(self, request, stack=None):
        if stack:
            return True

    def action(self, request, stack_id):
        obj = self.table.get_object_by_id(stack_id)
        name = self.table.get_object_display(obj)
        # api.heat.stack_delete(request, stack_id)

class RetryStack(tables.BatchAction):
    name = "retry"
    action_present = _("Retry")
    action_past = _("Scheduled Retry of")
    data_type_singular = _("Stack")
    data_type_plural = _("Stacks")
    classes = ('btn', 'btn-primary')

    def allowed(self, request, stack=None):
        if stack.stack_status == 'Create Failed':
            return True

    def action(self, request, stack_id):
        pass

class CloneStack(tables.BatchAction):
    name = "clone"
    action_present = _("Clone")
    action_past = _("Scheduled Clone of")
    data_type_singular = _("Stack")
    data_type_plural = _("Stacks")
    classes = ('btn', 'btn-primary')

    def allowed(self, request, stack=None):
        return True

    def action(self, request, stack_id):
        pass


class DeploymentsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Create Complete", True),
        ("Create Failed", False),
    )
    name = tables.Column("stack_name", verbose_name=_("Stack Name"),
                           link="horizon:project:stacks:detail",)
    created = tables.Column("creation_time",
                            verbose_name=_("Created"),
                            filters=(parse_isotime, timesince))
    updated = tables.Column("updated_time",
                            verbose_name=_("Updated"),
                            filters=(parse_isotime, timesince))
    status = tables.Column("stack_status",
                           filters=(title, replace_underscores),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)
    view = tables.Column("view",
                         verbose_name=_("View"))

    class Meta:
        name = "deployments"
        verbose_name = _("Deployments")
        status_columns = ["status", ]
        row_actions = (DeleteStack, )


class WorkflowTable(DeploymentsTable):
    class Meta:

        name = "workflows"
        verbose_name = _("Workflows")
        status_columns = ["status", ]

        row_actions = (RetryStack, )

class CloneTable(DeploymentsTable):
    class Meta:

        name = " "
        verbose_name = _(" ")
        status_columns = ["status", ]

        row_actions = (CloneStack, )



class LaunchCatalogue(tables.BatchAction):
    name = "launch"
    action_present = _("Launch")
    action_past = _("Scheduled Launch of")
    data_type_singular = _("Stack")
    data_type_plural = _("Stacks")
    classes = ('btn', 'btn-primary')

    def allowed(self, request, stack=None):
        return True

    def action(self, request, stack_id):
        pass

class CatFilterAction(tables.FilterAction):
    def filter(self, table, instances, filter_string):
        """ Naive case-insensitive search. """
        q = filter_string.lower()
        return [instance for instance in instances
                if q in instance.name.lower()]

class CataloguesTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Template Name"),)
    size = tables.Column("size", verbose_name=_("Size"))
    view = tables.Column("view", verbose_name=_("View"))

    class Meta:
        name = "catalogue"
        verbose_name = _("Catalogues")
        #status_columns = ["status", ]
        #table_actions = (LaunchCatalogue, DeleteStack,)
        #row_class = CataloguesUpdateRow
        table_actions = (CatFilterAction, )
        row_actions = (LaunchCatalogue, )

class LogsTable(tables.DataTable):

    date = tables.Column("date", verbose_name=_("Date"),classes=['log_date'])
    time = tables.Column("time", verbose_name=_("Time"),)
    nbr = tables.Column("nbr", verbose_name=_("Nbr"),)
    type = tables.Column("type", verbose_name=_("Type"),)
    location = tables.Column("location", verbose_name=_("Location"))
    description = tables.Column("description", verbose_name=_("Description"))

    class Meta:
        name = "logs"
        verbose_name = _("Logs")