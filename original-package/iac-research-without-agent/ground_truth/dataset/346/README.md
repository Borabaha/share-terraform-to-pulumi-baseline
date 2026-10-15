# Prompt 346

## Resources

aws_db_instance, aws_db_subnet_group, aws_subnet, aws_vpc

## Prompt

sets up a PostgreSQL database instance in AWS, specifying details like engine version, instance size, storage, and associated networking resources within a custom VPC and subnet.

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" = "postgres"
    with one "instance_class"
    with one "password"
    with one "username"

has one aws_db_subnet_group resource
has one aws_subnet
has one aws_vpc

