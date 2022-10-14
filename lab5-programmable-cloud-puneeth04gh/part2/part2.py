#!/usr/bin/env python3

import argparse
import os
import time
from pprint import pprint

import googleapiclient.discovery
import google.auth

# [START create_instance]
def create_instance(compute, project, zone, name, source_snapshot):
    # getsourceSnapshot = compute.snapshots().get(project = project , snapshot = snapshot_name).execute()
    # source_snapshot = getsourceSnapshot['selfLink']
    # # Get the latest Debian Jessie image.
    # image_response = compute.images().getFromFamily(
    #     project='ubuntu-os-cloud', family='ubuntu-2204-lts').execute()
    # source_disk_image = image_response['selfLink']

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
                    # 'sourceImage': source_disk_image,
                    'sourceSnapshot': source_snapshot
                    
                    
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

#
# Stub code - just lists all instances
#
# pylint: disable=maybe-no-member
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None

credentials, project = google.auth.default()
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

print("Your running instances are:")
for instance in list_instances(service, project, 'us-west1-b'):
    print(instance['name'])

# The name of the zone for this request.
zone = 'us-west1-b'  # TODO: Update placeholder value.

# Name of the persistent disk to snapshot.
disk = 'lab5-part1'  # TODO: Update placeholder value.

snapshot_body = {
    'name' : 'base-snapshot-lab5-part1'
}

print('Creating snapshot from first instance.')
snapshot_request = service.disks().createSnapshot(project=project, zone=zone, disk=disk, body=snapshot_body)
snapshot_response = snapshot_request.execute()
# pprint(snapshot_response)
wait_for_operation(service, project, zone, snapshot_response['name'])

getsourceSnapshot = service.snapshots().get(project = project , snapshot = snapshot_body['name']).execute()
source_snapshot = getsourceSnapshot['selfLink']

f = open("Time.md", "w")
print('Creating first instance from the snapshot.')
time_start = time.time()
operation = create_instance(service, project, zone, 'lab5-part2-instance1', source_snapshot)
# operation = create_instance(service, project, zone, 'lab5-part2-instance1', snapshot_body['name'])
wait_for_operation(service, project, zone, operation['name'])
duration = time.time() - time_start
f.write("Time taken for instance 1 = %s || \n" % duration)
get_request = service.instances().get(project=project, zone=zone, instance='lab5-part2-instance1')
get_response = get_request.execute()
fingerprint_val = get_response['tags']['fingerprint']
tag_body = {
    "items": [
            "allow-5000"
        ],
        "fingerprint" : fingerprint_val
}
set_tag_request = service.instances().setTags(project=project, zone=zone, instance='lab5-part2-instance1', body = tag_body)
set_tag_response = set_tag_request.execute()
print("Your blog is running in the link - http://{}:5000".format(get_response['networkInterfaces'][0]['accessConfigs'][0]['natIP']))

print('Creating second instance from the snapshot.')
time_start = time.time()
operation = create_instance(service, project, zone, 'lab5-part2-instance2', source_snapshot)
wait_for_operation(service, project, zone, operation['name'])
duration = time.time() - time_start
f.write("Time taken for instance 2 = %s || \n" % duration)
set_tag_request = service.instances().setTags(project=project, zone=zone, instance='lab5-part2-instance2', body = tag_body)
set_tag_response = set_tag_request.execute()
print("Your blog is running in the link - http://{}:5000".format(get_response['networkInterfaces'][0]['accessConfigs'][0]['natIP']))

print('Creating third instance from the snapshot.')
time_start = time.time()
operation = create_instance(service, project, zone, 'lab5-part2-instance3', source_snapshot)
wait_for_operation(service, project, zone, operation['name'])
duration = time.time() - time_start
f.write("Time taken for instance 3 = %s || \n" % duration)
f.close()
set_tag_request = service.instances().setTags(project=project, zone=zone, instance='lab5-part2-instance3', body = tag_body)
set_tag_response = set_tag_request.execute()
print("Your blog is running in the link - http://{}:5000".format(get_response['networkInterfaces'][0]['accessConfigs'][0]['natIP']))