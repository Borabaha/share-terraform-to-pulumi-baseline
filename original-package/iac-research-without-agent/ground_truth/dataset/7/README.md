# Prompt 7

## Resources

aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment

## Prompt

Create an elastic beanstalk environment that contains autoscaling settings using thresholds and CPU utilization. Name the iam_role "eb_ec2_role", the instance profile "eb_ec2_profile", and the elastic beanstalk application "my_api_app".

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

Has one "aws_elastic_beanstalk_environment" resource
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with several "setting" blocks that have "namespaces" set to either "aws:autoscaling:trigger" or "aws:autoscaling:asg", 
    with one "setting" block which has a "value" that references the "aws_iam_instance_profile" resource


