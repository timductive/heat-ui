import json
import logging
import re
import copy

from django.http import HttpResponse

from openstack_dashboard import api
from horizon import messages

from orchestration.stacks.sro import stack_info, resource_info

LOG = logging.getLogger(__name__)

class Stack(object):
    pass

def get_status_img(status, type):
    '''
    Sets the image url and in_progress action sw based on status.
    '''
    in_progress = True if re.search('IN_PROGRESS', status) else False
    failed = True if re.search('FAILED', status) else False

    if type == 'stack':
        if failed:
            return "/static/heat/img/stack-red.svg"
        elif in_progress:
            return "/static/heat/img/stack-gray.svg"
        else:
            return "/static/heat/img/stack-green.svg"
    elif type == 'server':
        if failed:
            return "/static/heat/img/server-red.svg"
        elif in_progress:
            return "/static/heat/img/server-gray.svg"
        else:
            return "/static/heat/img/server-green.svg"


def d3_data(request, stack_id=''):
    #Get Stack
    try:
        stack = api.heat.stack_get(request, stack_id)
        LOG.debug('get stack %s' % stack)
    except:
        stack = Stack()
        messages.error(request, _('Unable to get stack for stack id "%s".') % stack_id)

    #Get Resources
    try:
        resources = api.heat.resources_list(request, stack_id)
        LOG.debug('got resources %s' % resources)
    except:
        resources = []
        messages.error(request, _(
            'Unable to get resources for stack "%s".') % stack.stack_name)

    d3_data = {"nodes":[],"links":[]}
    group_ctr = 0
    instance_ctr = 0
    #FOR TESTING
    # stack.stack_status = 'CREATE_IN_PROGRESS'

    #First append Stack
    stack_node = {
        'stack_id':stack.id,
        'name':stack.stack_name,
        'status':stack.stack_status,
        'image':get_status_img(stack.stack_status, 'stack'),
        'image_size':60,
        'image_x':-20,
        'image_y':-20,
        'text_x':40,
        'text_y':".35em",
        'group':group_ctr,
        'instance':instance_ctr,
        'in_progress':True if re.search('IN_PROGRESS', stack.stack_status) else False,
        'info_box':stack_info(stack)
    }

    d3_data['nodes'].append(stack_node)
    group_ctr += 1
    instance_ctr += 1

    #Append all Resources
    for resource in resources:
        resource_node = {
            'name':resource.logical_resource_id,
            'status':resource.resource_status,
            'image':get_status_img(resource.resource_status, 'server'),
            'image_size':30,
            'image_x':-10,
            'image_y':-10,
            'text_x':25,
            'text_y':".35em",
            'group':group_ctr,
            'instance':instance_ctr,
            'in_progress':True if re.search('IN_PROGRESS', stack.stack_status) else False,
            'info_box':resource_info(resource)
        }

        d3_data['nodes'].append(resource_node)
        d3_data['links'].append({
            'source':resource_node['instance'],
            'target':stack_node['instance'],
            'value':1
        })
        instance_ctr += 1

    return json.dumps(d3_data)

def get_d3_data(request, stack_id=''):
    return HttpResponse(d3_data(request, stack_id=stack_id), content_type="application/json")