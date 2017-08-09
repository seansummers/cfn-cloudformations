from __future__ import print_function

import functools
import json

import boto3
import botocore

from botocore.exceptions import ClientError
from botocore.vendored import requests

json_dumps = functools.partial(json.dumps, separators=(',', ':'))

iam = boto3.resource('iam')


def cfnresponse_send(event,
                     context,
                     response_status,
                     response_data,
                     physical_resource_id=None,
                     reason=None):
    response_url = event['ResponseURL']
    log("INFO {} cfnresponse {}".format(response_status, response_url))
    logical_id = event['LogicalResourceId']
    if not physical_resource_id:
        physical_resource_id = logical_id
    response_body = {
        'Status':
        response_status,
        'Reason':
        reason or
        'See the details in CloudWatch Log Stream: {.log_stream_name}'.format(
            context),
        'PhysicalResourceId':
        physical_resource_id,
        'StackId':
        event['StackId'],
        'RequestId':
        event['RequestId'],
        'LogicalResourceId':
        logical_id,
        'Data':
        response_data,
    }
    response_body_json = json_dumps(response_body)
    log(response_body_json)
    try:
        response = requests.put(response_url, data=response_body_json)
        log("INFO cfnresponse {.reason}".format(response))
    except Exception as e:
        log("ERROR cfnresponse {}".format(e))


def handler(event, context=None):
    global log
    log = context.log if context else functools.partial(print, end='\n')
    log("INFO ENTER")
    log(json_dumps(event))
    request_type = event.get('RequestType')
    if request_type:
        physical_id = event.get('PhysicalResourceId')
        logical_id = event.get('LogicalResourceId')
        properties = event.get('ResourceProperties', {})
        name = properties.get('Name', logical_id)
        status = 'SUCCESS'
        data = {}
        reason = None
        log("INFO {} for {}".format(request_type, logical_id))
        try:
            if request_type in {'Create', 'Update'}:
                saml = properties.get('SAMLMetadata')
                if saml.startswith('https://'):
                    log("INFO Metadata {}".format(saml))
                    saml = requests.get(saml).text
                log("INFO creating/updating {}".format(physical_id if
                                                       physical_id else name))
                physical_id = iam.create_saml_provider(
                    SAMLMetadataDocument=saml, Name=name).arn
                log("INFO created/updated {}".format(physical_id))
            elif request_type == 'Delete':
                log("INFO deleting {}".format(physical_id))
                saml_provider = iam.SamlProvider(physical_id)
                physical_id = None
                saml_provider.delete()
        except ClientError as e:
            err = e.response['Error']
            log("ERROR {0[Code]} {0[Message]}".format(err))
            if request_type != 'Delete':
                status = 'FAILED'
            reason = err['Message']
        except botocore.exceptions.ParamValidationError as e:
            reason = '{}'.format(e)
            log("ERROR {}".format(reason))
            if request_type != 'Delete':
                status = 'FAILED'
        except requests.exceptions.ConnectionError as e:
            reason = '{}'.format(e)
            log("ERROR {}".format(reason))
            status = 'FAILED'
        cfnresponse_send(event, context, status, data, physical_id, reason)
    log("INFO EXIT")
