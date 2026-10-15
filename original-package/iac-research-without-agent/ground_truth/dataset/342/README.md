# Prompt 342

## Resources

aws_db_instance, aws_db_subnet_group, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

sets up an AWS environment with a main VPC, two subnets across different availability zones, and a security group to allow database access. It also configures a 200 GB 15.3 PostgresSQL RDS instance with public accessibility, linked to the defined subnets and security group, outputting the database endpoint for connectivity, with db.t4g.micro instance class, and with gp2 storage type.

## Difficulty

5

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage" = 20
    with one "engine" = "postgres"
    with one "instance_class" = db.t4g.micro
    with one "password"
    with one "username"
    with one publicly_accessible = true
    with one engine_version = "15.3"
    with one "storage_type" = "gp2"

has one aws_vpc

has more than one aws_subnet

has one security_group

has one db_subnet_group

