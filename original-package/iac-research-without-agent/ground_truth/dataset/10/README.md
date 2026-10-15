# Prompt 10

## Resources

aws_elastic_beanstalk_application, aws_elastic_beanstalk_application_version, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment, aws_s3_bucket, aws_s3_object

## Prompt

Create an elastic beanstalk environment with an elastic beanstalk application version. Name the iam_role "eb_ec2_role", the instance profile "eb_ec2_profile", the elastic beanstalk application "myapp", the bucket "sampleapril26426", the object "examplebucket_object", and the application version "version".

## Difficulty

5

## Intent

Has one "aws_iam_role" resource
    with "name"
    with "assume_role_policy" and "Service" set to "ec2.amazonaws.com"

Has one "aws_iam_role_policy_attachment" resource
    with "role" referencing the "aws_iam_role"
    with "policy_arn" set to "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"

Has one "aws_iam_instance_profile" resource
    with "name"
    with "role" referencing the "aws_iam_role" resource

Has one "aws_elastic_beanstalk_application" resource
    with "name"

Has one "aws_s3_bucket" resource
    with "bucket"

Has one "aws_s3_object" resource
    with "key"
    with "source"
    with "bucket" referencing the "aws_s3_bucket" resource

Has one "aws_elastic_beanstalk_application_version" resource
    with "name
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "bucket" referencing the "bucket" from the "aws_s3_object" resource
    with "key" referencing the "key" from the "aws_s3_object" resource

Has one "aws_elastic_beanstalk_environment" resource
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with "version_label" referencing the "aws_elastic_beanstalk_application_version" resource
    with one "setting" block which has a "value" that references the "aws_iam_instance_profile" resourc

