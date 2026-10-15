# Prompt 347

## Resources

aws_db_instance, aws_db_subnet_group, aws_subnet, aws_vpc

## Prompt

sets up a PostgreSQL database instance in AWS, specifying details like engine version, instance size, storage, and associated networking resources within a custom VPC and subnet. the backup retention period should be 5, and the backup window should be from 3 AM to 6 AM

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" = "postgres"
    with one "instance_class"
    with one "password"
    with one "username"
    with one backup_retention_period = 5
    with one backup_window.constant_value = "03:00-06:00"

has one aws_db_subnet_group resource
has one aws_subnet
has one aws_vpc

