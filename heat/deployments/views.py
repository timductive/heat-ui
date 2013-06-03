from django.views import generic

class IndexView(generic.TemplateView):
  #  table_class = ThermalCataloguesTable
     template_name = 'heat/deployments/index.html'