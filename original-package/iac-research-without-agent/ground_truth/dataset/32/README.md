# Prompt 32

## Resources

aws_elastic_beanstalk_application, aws_iam_role

## Prompt

Create an Elastic Beanstalk application with an app version lifecycle. Retain the version for 5 days

## Difficulty

3

## Intent

Has one "aws_elastic_beanstalk_application" resource
    with "name"
    with "appversion_lifecycle" block

Has one "aws_iam_role" resource
    with "name"
    with "assume_role_policy" and "Service" set to "elasticbeanstalk.amazonaws.com"

