# Prompt 12

## Resources

aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment, aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Configure Blue/Green deployment with Route53 resources to navigate traffic between Elastic Beanstalk Environments. Name the environments "blue" and "green" and implement a Weighted Routing Policy for the records

## Difficulty

6

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

Has two "aws_elastic_beanstalk_environment" resources
    each are provisioned in different regions
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with one "setting" block which has a "value" that references the "aws_iam_instance_profile" resource

Has one "aws_route53_zone" resource
    with "name"

Has two "aws_route53_record" resources
    each are provisioned in different regions
    with "name"
    with "type"
    with "ttl"
    with "zone_id" referencing the "aws_route53_zone" resource
    with "set_identifier"
    with "weighted_routing_policy" block that contains "weight" as a non-zero number
    with "records" referencing one of the "aws_elastic_beanstalk_environment" resources

