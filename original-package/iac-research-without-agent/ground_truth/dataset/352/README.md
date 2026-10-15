# Prompt 352

## Resources

aws_db_option_group

## Prompt

defines an AWS RDS option group named "option-group-pike" with major engine version 11, and use the sqlserver-ee engine. It should have options for "SQLSERVER_AUDIT" and "TDE". IAM_ROLE_ARN and S3_BUCKET_ARN are included under SQLSERVER_AUDIT option

## Difficulty

3

## Intent

Has one "aws_db_option_group" resource
    with one "engine_name" = "sqlserver-ee"
    with one "major_engine_version" = "11.00"
    with options for "SQLSERVER_AUDIT" and "TDE"
    with specific settings for "IAM_ROLE_ARN" and "S3_BUCKET_ARN"

