# `AWS::CloudFormation::CustomResource`

This GitHub project contains CloudFormation templates for creating 
Lambda Backed Custom Resources for CloudFormation.

## `Custom:::SamlProvider`

### Reference

*Custom::SamlProvider* is exported to the Instance Store for easy 
reference in other stacks using *Fn::ImportValue*.

    --- # sample-stack.yaml
    Resources:
      MySAMLProvider:
        Type: Custom::SamlProvider
        Version: 1.0
        Properties:
            ServiceToken: !ImportValue 'Custom::SamlProvider'
            SAMLMetadata: https://someprovider/Metadata.xml
            Name: samlProviderName
    ...

The `Name` parameter is optional, and the LogicalId (*`MySAMLProvider`
in this example*) is used if omitted.

### Installation

**aws cloudformation package** the Cloudformation template in your account:

    aws cloudformation package \
    --s3-bucket <your S3 bucket> \
    --s3-prefix <S3 prefix, without trailing /> \
    --template-file cfnSamlProvider.yaml \
    --output-template-file stack-cfnSamlProvider.yaml

The next step creates objects in your AWS account:

    aws cloudformation deploy \
    --template-file stack-cfnSamlProvider.yaml \
    --stack-name cfnSamlProvider \
    --capabilities CAPABILITY_IAM [--no-execute-changeset]

If you add `--no-execute-changeset`, you will be able to see the changes 
that the parent stack will make, and will be able to execute the ChangeSet
with an account that has IAM permissions. Otherwise, you'll need
IAM permissions to successfully run **aws cloudformation deploy**.
