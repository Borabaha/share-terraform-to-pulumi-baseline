# Prompt 6

## Resources

aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment

## Prompt

Create a basic elastic beanstalk environment with a elastic beanstalk application. Name the iam_role "eb_ec2_role", the instance profile "eb_ec2_profile", and the elastic beanstalk application "my_application"

## Difficulty

4

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

Has one "aws_elastic_beanstalk_environment" resource
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with one "setting" block which has a "value" that references the "aws_iam_instance_profile" resource


