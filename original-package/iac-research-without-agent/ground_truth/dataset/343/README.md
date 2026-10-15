# Prompt 343

## Resources

aws_db_instance, aws_security_group, random_string

## Prompt

 creates a MySQL database instance on AWS RDS with a public access security group and a randomly generated password.

## Difficulty

4

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" = "mysql"
    with one "instance_class" and a valid instance class type
    with one "password"
    with one "username"

has one security_group

has one random_string

