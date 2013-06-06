from datetime import datetime

from django.views import generic

class IndexView(generic.TemplateView):
    template_name = 'heat/logging/logging.html'

    def get_context_data(self, **kwargs):
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")

        context = super(IndexView, self).get_context_data(**kwargs)

        context['today'] = today

        return context