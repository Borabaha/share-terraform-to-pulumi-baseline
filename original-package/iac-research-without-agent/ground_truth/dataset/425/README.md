# Prompt 425

## Resources

aws_efs_file_system, aws_efs_mount_target, aws_subnet, aws_vpc

## Prompt

create a AWS EFS with mount target

## Difficulty

3

## Intent

Have one "aws_efs_file_system" resource

Have one "aws_efs_mount_target" resource
with one "file_system_id"
with one "subnet_id"

Have one "aws_subnet" resource
(FOR SUBNET_ID IN MOUNT_TARGET)

Have one "aws_vpc" resource
(FOR VPC_ID IN "AWS_SUBNET")

