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

    lb_instance = True if re.search('LoadBalancer', type) else False
    db_instance = True if re.search('DBInstance', type) else False
    if lb_instance:
        if failed:
            return "/static/heat/img/lb-red.svg"
        elif in_progress:
            return "/static/heat/img/lb-gray.gif"
        else:
            return "/static/heat/img/lb-green.svg"
    elif db_instance:
        if failed:
            return "/static/heat/img/db-red.svg"
        elif in_progress:
            return "/static/heat/img/db-gray.gif"
        else:
            return "/static/heat/img/db-green.svg"
    elif type == 'stack':
        if failed:
            return "/static/heat/img/stack-red.svg"
        elif in_progress:
            return "/static/heat/img/stack-gray.gif"
        else:
            return "/static/heat/img/stack-green.svg"
    else:
        if failed:
            return "/static/heat/img/server-red.svg"
        elif in_progress:
            return "/static/heat/img/server-gray.gif"
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



    d3_data = {"nodes":[], "stack":{}}

    #FOR TESTING
    # stack['stack_status'] = 'CREATE_IN_PROGRESS'
    # r1 = copy.copy(resources[1])
    # r1['logical_resource_id'] = 'test1'
    # r1['resource_status'] = 'CREATE_IN_PROGRESS'
    # r2 = copy.copy(resources[1])
    # r2['logical_resource_id'] = 'test2'
    # resources.append(r1)
    # resources.append(r2)
    # resources[0]['required_by'].append('test1')
    # resources[0]['required_by'].append('test2')
    # print resources[0].get('logical_resource_id')
    # resources.pop(5)
    # resources.pop(2)
    # resources.pop(0)

    #1
    # stack['stack_status'] = 'CREATE_IN_PROGRESS'
    # resources = [resources[0]]
    # resources[0]['resource_status'] = 'CREATE_IN_PROGRESS'

    #2
    # stack['stack_status'] = 'CREATE_IN_PROGRESS'
    # resources.pop(5)
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_IN_PROGRESS'
    # resources[2]['resource_status'] = 'CREATE_IN_PROGRESS'
    # resources[3]['resource_status'] = 'CREATE_IN_PROGRESS'
    # resources[4]['resource_status'] = 'CREATE_IN_PROGRESS'

    #3
    # stack['stack_status'] = 'CREATE_IN_PROGRESS'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'CREATE_COMPLETE'
    # resources[4]['resource_status'] = 'CREATE_COMPLETE'
    # resources[5]['resource_status'] = 'CREATE_IN_PROGRESS'

    #4
    # stack['stack_status'] = 'CREATE_COMPLETE'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'CREATE_COMPLETE'
    # resources[4]['resource_status'] = 'CREATE_COMPLETE'
    # resources[5]['resource_status'] = 'CREATE_COMPLETE'

    #5
    # stack['stack_status'] = 'UPDATE_IN_PROGRESS'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'UPDATE_IN_PROGRESS'
    # resources[4]['resource_status'] = 'UPDATE_IN_PROGRESS'
    # resources[5]['resource_status'] = 'CREATE_COMPLETE'

    #6
    # stack['stack_status'] = 'UPDATE_COMPLETE'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'UPDATE_COMPLETE'
    # resources[4]['resource_status'] = 'UPDATE_COMPLETE'
    # resources[5]['resource_status'] = 'CREATE_COMPLETE'

    #7
    # stack['stack_status'] = 'UPDATE_COMPLETE'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'UPDATE_COMPLETE'
    # resources[4]['resource_status'] = 'UPDATE_COMPLETE'
    # resources.pop(5)

    #8
    # stack['stack_status'] = 'UPDATE_COMPLETE'
    # resources[0]['resource_status'] = 'CREATE_COMPLETE'
    # resources[1]['resource_status'] = 'CREATE_COMPLETE'
    # resources[2]['resource_status'] = 'CREATE_COMPLETE'
    # resources[3]['resource_status'] = 'CREATE_COMPLETE'
    # resources[4]['resource_status'] = 'CREATE_COMPLETE'
    # resources[5]['resource_status'] = 'CREATE_COMPLETE'

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
        'in_progress':True if re.search('IN_PROGRESS', stack.get('stack_status')) else False,
        'info_box':stack_info(stack, get_status_img(stack.get('stack_status'), 'stack'))
    }
    #
    d3_data['stack'] = stack_node

    #Append all Resources
    for resource in resources:
        resource_node = {
            'name':resource.get('logical_resource_id'),
            'status':resource.get('resource_status'),
            'image':get_status_img(resource.get('resource_status'), resource.get('resource_type')),
            'required_by':resource.get('required_by'),
            'image_size':50,
            'image_x':-25,
            'image_y':-25,
            'text_x':35,
            'text_y':".35em",
            'in_progress':True if re.search('IN_PROGRESS', resource.get('resource_status')) else False,
            'info_box':resource_info(resource)
        }
        d3_data['nodes'].append(resource_node)

    return json.dumps(d3_data)

def get_d3_data(request, stack_id=''):
    return HttpResponse(d3_data(request, stack_id=stack_id), content_type="application/json")