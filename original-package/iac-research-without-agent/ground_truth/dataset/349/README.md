# Prompt 349

## Resources

aws_db_instance, aws_db_subnet_group, aws_subnet, aws_vpc

## Prompt

sets up a PostgreSQL database instance in AWS, specifying details like engine version, instance size, storage, and associated networking resources within a custom VPC and subnet. the database should allow major version upgrade, automatically do minor version upgrade, and should not be publicly accessible.

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" = "postgres"
    with one "instance_class"
    with one "password"
    with one "username"
    with one allow_major_version_upgrade = true
    with one auto_minor_version_upgrade = true
    with one publicly_accessible = false

has one aws_db_subnet_group resource
has one aws_subnet
has one aws_vpc

