# Prompt 25

## Resources

aws_db_instance, aws_db_instance, aws_elastic_beanstalk_application, aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment, aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Configure multi-region application deployment with Route 53 resources to manage a domain and direct traffic to Elastic Beanstalk environments that have a connected RDS database. Provision the respective resources in either "us-east-1" or "eu-west-1" regions and name the aliases "us-east-1" and "eu-west-1" respectively. Name the environments "myenv_us_east" and "myenv_eu_west", the applications "myapp_us_east" and "myapp_eu_west", the instance profile "eb_ec2_profile3", and the databases "main_db_us_east" and "main_db_eu_west"

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

Has two "aws_elastic_beanstalk_application" resource provisioned in different regions
    with "name"

Has two "aws_elastic_beanstalk_environment" resources provisioned in different regions
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with a "setting" block which has a "value" that references the "aws_iam_instance_profile" resource
    with a "setting" block that has a "value"  that references the "address" from one of the "db_instance" resource
    with a "setting" block that has a "value"  that references the "username" from one of the "db_instance" resource 
    with a "setting" block that has a "value"  that references the "password" from one of the "db_instance" resource 

Has two "aws_db_instance" resources provisioned in different regions
    with "instance_class"
    with "allocated_storage"
    with "engine"
    with "username"
    with "password"
    with "backup_retention_period" set to a non-zero number
    with "skip_final_snapshot"


Has one "aws_route53_zone" resource
    with "name"

Has two "aws_route53_record" resources provisioned in different regions
    with "name"
    with "type"
    with "ttl"
    with "zone_id" referencing the "aws_route53_zone" resource
    with "set_identifier"
    with "records" referencing one of the "aws_elastic_beanstalk_environment" resource
    with "latency_routing_policy" containing "region" 




