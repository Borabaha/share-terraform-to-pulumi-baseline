# Prompt 14

## Resources

aws_db_instance, aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment

## Prompt

Configure an Elastic Beanstalk environment that is linked to a relational database instance. Call the db_instance "default" and the instance profile "eb_ec2_profile"

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


Has one "aws_elastic_beanstalk_environment" resource
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with one "setting" block which has a "value" that references the "aws_iam_instance_profile" resource
    with two "setting" blocks that have "namespace" set to "aws:autoscaling:asg"
    with a "setting" block that has a "value"  that references the "address" from the production "db_instance" resource
    with a "setting" block that has a "value"  that references the "username" from the "db_instance" resource 
    with a "setting" block that has a "value"  that references the "password" from the "db_instance" resource 

Has a "aws_db_instance" resource
    with "identifier"
    with "instance_class"
    with "allocated_storage"
    with "engine"
    with "username"
    with "password"
    with "backup_retention_period" set to a non-zero number
    with "skip_final_snapshot"


