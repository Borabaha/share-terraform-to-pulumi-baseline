# Prompt 307

## Resources

aws_backup_plan, aws_backup_selection, aws_backup_vault, aws_iam_role, aws_iam_role_policy_attachment, aws_instance, aws_iam_policy_document

## Prompt

An AWS service that provisions an EC2 instance and backs it up every day at midnight. Accomplish this using the following services: AWS EC2, AWS Backup. Add any necessary services.

## Difficulty

5

## Intent

have one "aws_ami" data resource
have one "aws_instance" resource
  with "ami" argument linking to the aws_ami data resource
  with "instance_type" argument
have one "aws_backup_plan" resource
  with "name" argument
  with "rule" argument block
    with "rule_name" argument
    with "target_vault_name" argument linking to backup_vault
    with "schedule" argument with value "cron(0 0 * * ? *)"
  with "advanced_backup_setting" argument block
    with "backup_options" argument block
      with "WindowsVSS" argument
    with "resource_type" argument with value "EC2"
have one "aws_backup_vault" resource
  with "name" argument
have one "aws_backup_selection" resource
  with "iam_role_arn" argument
  with "name" argument
  with "plan_id" argument linking to aws_backup_plan resource
  with "resources" argument including the aws_instance resource

