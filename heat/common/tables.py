from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import title, timesince

from horizon import tables
from horizon.utils.filters import replace_underscores, parse_isotime





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