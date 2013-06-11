from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe
from django.template.defaultfilters import title

from horizon.utils.filters import replace_underscores

class Breadcrumbs(TemplateView):

    def get_context_data(self, **kwargs):
        request = self.request
        url = request.get_full_path()

        crumbs = url.split('/')
        last_crumb = crumbs[-3:-1]
        current_crumb = last_crumb[0]
        stack_name = last_crumb[1]
        crumbs = crumbs[1:3]
        breadcrumbs = ''
        build_url = ''
        for crumb in crumbs:
            if crumb:
                build_url+='/'+crumb
                if crumb != 'heat':
                    breadcrumbs+='<a href="'+build_url+'">'+title(replace_underscores(crumb))+'</a> |'

        # build_url+='/'+current_crumb+'/'+stack_name+'/'
        # breadcrumbs+=' <a href="'+build_url+'">'+title(replace_underscores(stack_name+' '+current_crumb))+'</a>'

        breadcrumbs+=' '+title(replace_underscores(stack_name+' '+current_crumb))

        breadcrumbs = mark_safe(breadcrumbs)
        context = super(Breadcrumbs, self).get_context_data(**kwargs)
        context['breadcrumbs'] = breadcrumbs
        return context