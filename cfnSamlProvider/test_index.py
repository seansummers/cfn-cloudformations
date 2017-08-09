import index

event = {
  "RequestId": "unique id for this create request",
  "ResponseURL": "pre-signed-url-for-create-response",
  "ResourceType": "Custom::MyCustomResourceType",
  "StackId": "arn:aws:cloudformation:us-east-2:namespace:stack/stack-name/guid",
}

def test_missing_everything():
    index.handler(event)

def test_delete_nonexisting_missing_physicalid():
    event.update({
        'RequestType': 'Delete',
    })
    index.handler(event)

def test_delete_nonexisting():
    event.update({
        'PhysicalResourceId': 'arn:aws:iam::123456789012:saml-provider/samltestprovider',
    })
    index.handler(event)

def test_update_nonexisting_missing_logicalid():
    event.update({
        'RequestType': 'Update',
        'PhysicalResourceId': 'arn:aws:iam::123456789012:saml-provider/samltestprovider',
    })
    index.handler(event)

def test_update_nonexisting():
    event.update({
        'LogicalResourceId': 'samltestprovider',
    })
    index.handler(event)


if __name__ == '__main__':
    test_missing_everything()
    test_delete_nonexisting_missing_physicalid()
    test_delete_nonexisting()
    test_update_nonexisting_missing_logicalid()
    test_update_nonexisting()
