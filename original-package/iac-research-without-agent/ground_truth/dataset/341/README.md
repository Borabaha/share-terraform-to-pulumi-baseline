# Prompt 341

## Resources

aws_db_instance, aws_db_subnet_group, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

sets up an AWS environment with a main VPC, two subnets across different availability zones, and a security group to allow database access. It also configures a 20 GB 15.3 PostgresSQL RDS instance with public accessibility, linked to the defined subnets and security group, outputting the database endpoint for connectivity.

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" and a valid engine value
    with one "instance_class" and a valid instance class type
    with one "password"
    with one "username"
    with one publicly_accessible = true

has one aws_vpc

has more than one aws_subnet

has one security_group

has one db_subnet_group

