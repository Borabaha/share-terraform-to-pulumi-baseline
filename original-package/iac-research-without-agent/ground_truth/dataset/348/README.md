# Prompt 348

## Resources

aws_db_instance, aws_db_subnet_group, aws_subnet, aws_vpc

## Prompt

sets up a 5 GB PostgreSQL database instance in AWS, specifying details like engine version, instance size, storage, and associated networking resources within a custom VPC and subnet. The max allocated storage should be 50 GB, and the maintainance window should be 0:00 to 3:00 AM on monday.

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage" = 5
    with one "engine" = "postgres"
    with one "instance_class"
    with one "password"
    with one "username"
    with one "max_allocated_storage" = 50
    with one "maintenance_window" = "Mon:00:00-Mon:03:00"

has one aws_db_subnet_group resource
has one aws_subnet
has one aws_vpc

