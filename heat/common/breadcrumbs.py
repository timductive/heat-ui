from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe

class Breadcrumbs(TemplateView):

    def get_context_data(self, **kwargs):
        request = self.request
        url = request.get_full_path()

        crumbs = url.split('/')
        crumbs = crumbs[1:3]
        breadcrumbs = ''
        build_url = ''
        for crumb in crumbs:
            if crumb:
                build_url+='/'+crumb
                if crumb == 'heat':
                    breadcrumbs+='<a href="/heat/">Stacks</a> | '
                else:
                    breadcrumbs+='<a href="'+build_url+'">'+crumb+'</a> '

        breadcrumbs = mark_safe(breadcrumbs)
        context = super(Breadcrumbs, self).get_context_data(**kwargs)
        context['breadcrumbs'] = breadcrumbs
        return context