#!/usr/bin/env python

import argparse
import os
import time

import googleapiclient.discovery
from six.moves import input
from pprint import pprint
import googleapiclient.discovery
import google.auth
from oauth2client.client import GoogleCredentials

# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/f1-micro" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                    
                    
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }]
        }
    }
    

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]


# [START run]
def main(project, zone, instance_name, wait=True):
    compute = googleapiclient.discovery.build('compute', 'v1')

    print('Creating instance.')

    operation = create_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(instance['networkInterfaces'])
        print(' - ' + instance['name'])

if __name__ == '__main__':
    credentials, project = google.auth.default()

    service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
    zone = 'us-west1-b'
    instance = 'lab5-part1'
    firewall_body = {
        "name": "allow-5000",
        "description": "Firewall rule to allow 5000 port",
        "targetTags": [
            "allow-5000"
        ],
        "allowed": [
            {
            "IPProtocol": "tcp",
            "ports": [
                    "5000"
                ]
            }
        ]
    }

    firewall_list = service.firewalls().list(project=project).execute() 
    is_5000_present = False
    for fw_list in firewall_list['items']:
        if(fw_list['name'] == "allow-5000"):
            is_5000_present = True

    if is_5000_present == False:
        request = service.firewalls().insert(project=project, body=firewall_body)
        response = request.execute()
        pprint(response)
    else:
        print("allow-5000 firewall is already present")

    main(project,zone,instance)

    print("Setting the tag")
    get_request = service.instances().get(project=project, zone=zone, instance=instance)
    get_response = get_request.execute()
    fingerprint_val = get_response['tags']['fingerprint']
    tag_body = {
        "items": [
                "allow-5000"
            ],
            "fingerprint" : fingerprint_val
    }
    set_tag_request = service.instances().setTags(project=project, zone=zone, instance=instance, body = tag_body)
    set_tag_response = set_tag_request.execute()
    # pprint(set_tag_response)
    print("Your blog is running in the link - http://{}:5000".format(get_response['networkInterfaces'][0]['accessConfigs'][0]['natIP']))
#[END run]