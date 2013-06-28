import json
import logging
import re
import copy
import httplib2

from django.http import HttpResponse
from django.conf import settings

from openstack_dashboard.api.base import url_for
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

def get_rs_token(request):
    #Setup RS Token
    rs_user = request.user.username
    rs_password = getattr(settings, 'RACKSPACE_PASSWORD', False)
    url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'
    data = {}
    data['auth'] = {}
    data['auth']['passwordCredentials'] = {'username':rs_user,'password':rs_password}
    h = httplib2.Http(".cache")
    resp, content = h.request(
        uri=url,
        method='POST',
        headers={'Content-Type': 'application/json; charset=UTF-8'},
        body=json.dumps(data),
        )
    content = json.loads(content)
    rs_token = content.get('access').get('token').get('id')
    return rs_token

def get_stacks(request):
    endpoint = url_for(request, 'orchestration')
    stacks_list_url = endpoint + '/stacks?limit=20'
    rs_user = request.user.username
    rs_password = getattr(settings, 'RACKSPACE_PASSWORD', False)

    headers = {}
    headers['X-Auth-User'] = rs_user
    headers['X-Auth-Token'] = get_rs_token(request)
    headers['X-Auth-Key'] = rs_password
    headers['Content-Type'] = 'application/json; charset=UTF-8'

    h = httplib2.Http(".cache")
    resp, content = h.request(
        uri=stacks_list_url,
        method='GET',
        headers=headers,
        )
    stacks = json.loads(content)
    return stacks

def get_stack(request, stack_id):
    endpoint = url_for(request, 'orchestration')
    stack_url = endpoint + '/stacks/' + stack_id
    rs_user = request.user.username
    rs_password = getattr(settings, 'RACKSPACE_PASSWORD', False)

    headers = {}
    headers['X-Auth-User'] = rs_user
    headers['X-Auth-Token'] = get_rs_token(request)
    headers['X-Auth-Key'] = rs_password
    headers['Content-Type'] = 'application/json; charset=UTF-8'

    h = httplib2.Http(".cache")
    resp, content = h.request(
        uri=stack_url,
        method='GET',
        headers=headers,
        )
    stack = json.loads(content)
    return stack.get('stack')

def get_resources(request, stack_name, stack_id):
    endpoint = url_for(request, 'orchestration')
    resources_list_url = endpoint + '/stacks/' + stack_name + '/' + stack_id + '/resources'
    rs_user = request.user.username
    rs_password = getattr(settings, 'RACKSPACE_PASSWORD', False)

    headers = {}
    headers['X-Auth-User'] = rs_user
    headers['X-Auth-Token'] = get_rs_token(request)
    headers['X-Auth-Key'] = rs_password
    headers['Content-Type'] = 'application/json; charset=UTF-8'

    h = httplib2.Http(".cache")
    resp, content = h.request(
        uri=resources_list_url,
        method='GET',
        headers=headers,
        )
    resources = json.loads(content)
    return resources.get('resources')


def d3_data(request, stack_id=''):
    stack = get_stack(request, stack_id)
    stack_name = stack.get('stack_name','')
    resources = get_resources(request, stack_name, stack_id)



    d3_data = {"nodes":[],"links":[]}
    group_ctr = 0
    instance_ctr = 0
    #FOR TESTING
    # stack['stack_status'] = 'CREATE_IN_PROGRESS'

    print 'START D3 API HERE'
    print stack
    print resources


    #First append Stack
    stack_node = {
        'stack_id':stack.get('id'),
        'name':stack.get('stack_name'),
        'status':stack.get('stack_status'),
        'image':get_status_img(stack.get('stack_status'), 'stack'),
        'image_size':60,
        'image_x':-30,
        'image_y':-30,
        'text_x':40,
        'text_y':".35em",
        'group':group_ctr,
        'instance':instance_ctr,
        'in_progress':True if re.search('IN_PROGRESS', stack.get('stack_status')) else False,
        'info_box':stack_info(stack)
    }

    d3_data['nodes'].append(stack_node)
    group_ctr += 1
    instance_ctr += 1

    #Append all Resources
    for resource in resources:
        resource_node = {
            'name':resource.get('logical_resource_id'),
            'status':resource.get('resource_status'),
            'image':get_status_img(resource.get('resource_status'), 'server'),
            'image_size':30,
            'image_x':-15,
            'image_y':-15,
            'text_x':25,
            'text_y':".35em",
            'group':group_ctr,
            'instance':instance_ctr,
            'in_progress':True if re.search('IN_PROGRESS', resource.get('resource_status')) else False,
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