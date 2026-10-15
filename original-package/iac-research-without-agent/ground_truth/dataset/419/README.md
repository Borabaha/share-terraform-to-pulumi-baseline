# Prompt 419

## Resources

aws_db_instance, aws_kms_key

## Prompt

create an aws database that Managed Master Passwords via Secrets Manager, with specific KMS Key

## Difficulty

2

## Intent

Has one "aws_db_instance" resource
    with one "allocated_storage"
    with one "engine" and a valid engine value
    with one "instance_class" and a valid instance class type
    with one "username"
    with one manage_master_user_password
    with one "master_user_secret_kms_key_id"  
 
has one "aws_kms_key"

