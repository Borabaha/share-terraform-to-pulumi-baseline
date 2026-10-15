# Prompt 325

## Resources

aws_db_instance, random_id, random_password

## Prompt

Create an 20GB mysql on aws with randomly generated id and password

## Difficulty

3

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage" = 20
    with one "engine" = mysql
    with one "instance_class" and a valid instance class type
    with one "password"
    with one "username"
    with skip_final_snapshot = true
    with identifier generated from random_id
    with password generated from random_password

has one random_id resrource

has one random_password resource

