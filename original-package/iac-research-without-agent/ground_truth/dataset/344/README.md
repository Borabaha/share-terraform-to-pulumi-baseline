# Prompt 344

## Resources

aws_db_instance, aws_security_group, random_string

## Prompt

 creates a 200 GB 5.7 MySQL database instance on AWS RDS with db.t3.micro instance class, a public access security group and a randomly generated password.

## Difficulty

4

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage" = 200
    with one "engine" = "mysql"
    with one "instance_class" = "db.t3.micro"
    with one "password"
    with one "username"
    with one "engine_version" = "5.7"

has one security_group

has one random_string

