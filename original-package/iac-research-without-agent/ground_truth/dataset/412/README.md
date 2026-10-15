# Prompt 412

## Resources

aws_db_instance, aws_db_instance

## Prompt

create an aws sql, and make a replica of it

## Difficulty

2

## Intent

Has two "aws_db_instance" resources

resource 1:
with one "allocated_storage"
with one "engine" and a valid engine value
with one "instance_class" and a valid instance class type
with one "password"
with one "username"

resource 2:
with one "instance_class"
with one "replicate_source_db" = "aws_db_instance.resource1.identifier"

