# Prompt 19

## Resources

aws_db_instance, aws_db_subnet_group, aws_elastic_beanstalk_application, aws_elastic_beanstalk_environment, aws_elastic_beanstalk_environment, aws_iam_instance_profile, aws_iam_role, aws_iam_role_policy_attachment, aws_internet_gateway, aws_route_table, aws_route_table_association, aws_route_table_association, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Configure an AWS VPC with internet gateway, two public subnets, a security group, and a route table associated with the public subnets. Then connect these resources to two Elastic Beanstalk environments. These environments are also connected to a shared RDS database that is linked to the subnets. Name the database "shared_rds", the security group "eb_env_sg", the vpc "eb_vpc", and the subnets "eb_subnet_public_1" and "eb_subnet_public_2"

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

Has one "aws_vpc" resource
    with "cidr_block" set to a valid value

Has one "aws_internet_gateway" resource
    with "vpc_id" referencing the "aws_vpc" resource

Has two "aws_subnet" resources
    with "vpc_id" referencing the "aws_vpc" resource
    with "cidr_block" set to a valid value
    with "availability_zone" set to a zone within the region

Has one "aws_security_group" resource
     with "vpc_id" referencing the "aws_vpc" resource
     with "ingress" blocks
     with "egress" block

Has one "aws_db_subnet_group" resource
     with "subnet_ids" referencing the "aws_subnet" resources

Has one "aws_route_table" resources
     with "vpc_id" referencing the "aws_vpc" resource
     with the "route" block containing "gateway_id" referencing the "aws_internet_gateway" resource

Has two "aws_route_table_association" resources
     with "subnet_id" referencing one of the "aws_subnet" resources
     with "route_table_id" referencing the "aws_route_table" resource

Has one "aws_elastic_beanstalk_application" resource
    with "name"


Has two "aws_elastic_beanstalk_environment" resources
    with "name"
    with "application" referencing the "aws_elastic_beanstalk_application" resource
    with "solution_stack_name"
    with a "setting" block that has a "value" that references the "aws_iam_instance_profile" resource
    with a "setting" block that has a "value" that references the "id" from all the "aws_subnet" resources
    with a "setting" block that has a "value" that references the "id" from the "aws_vpc" resource
    with a "setting" block that has a "value" that references the "id" from the "aws_security_group" resource
    with a "setting" block that has a "value" that references the "address" from the "db_instance" resource
    with a "setting" block that has a "value" that references the "username" from the "db_instance" resource 
    with a "setting" block that has a "value" that references the "password" from the "db_instance" resource 

Has a "aws_db_instance" resource
    with "instance_class"
    with "allocated_storage"
    with "engine"
    with "username"
    with "password"
    with "backup_retention_period" set to a non-zero number
    with "skip_final_snapshot"
    with "db_subnet_group_name" referencing the "aws_db_subnet_group" resource
    with "vpc_security_group_ids" referencing the "aws_security_group" resource

