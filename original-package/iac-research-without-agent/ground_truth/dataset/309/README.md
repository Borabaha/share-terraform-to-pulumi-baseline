# Prompt 309

## Resources

aws_backup_plan, aws_backup_selection, aws_backup_vault, aws_iam_role, aws_iam_role_policy_attachment, aws_instance, aws_key_pair, aws_ami, aws_iam_policy_document

## Prompt

An AWS EC2 key pair resource with public_key argument specified with a path to key file being "./key.pub". An AWS EC2 instance with the amazon linux 2023 x86-64 machine image with a key_name argument specified by the key pair resource and "t2.micro" instance_type. An AWS Backup plan resource, a rule argument block with a schedule of every day midnight, and an target_vault_name argument linking to the Backup vault resource, a lifecycle argument block with delete_after 7 days, and an advanced_back_up_setting argument block to specify the resource_type that is being backed up. A backup vault to use for the backup, and a backup selection according to the backup plan that backs up the EC2 instance. An IAM role for the backup selection, with an attached policy with ARN "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup".

## Difficulty

5

## Intent

have one "aws_ami" resource
  with "filter" argument block
    with "name" argument
    with "values" argument with value "al2023-ami-2023.*-x86_64"
have one "aws_key_pair" resource
  with "public_key" argument
have one "aws_instance" resource
  with "ami" argument linking to ami resource
  with "instance_type" argument with value "t2.micro"
  with "key_name" argument linking to key_pair resource
have one "aws_backup_plan" resource
  with "name" argument
  with "rule" argument block
    with "rule_name" argument
    with "target_vault_name" argument linking to backup_vault
    with "schedule" argument with value "cron(0 0 * * ? *)"
  with "lifecycle" argument block
    with "delete_after" argument with value 7
  with "advanced_backup_setting" argument block
    with "backup_options" argument block
      with "WindowsVSS" argument with value "enabled"
    with "resource_type" argument with value "EC2"
have one "aws_backup_vault" resource
  with "name" argument
have one "aws_backup_selection" resource
  with "iam_role_arn" argument
  with "name" argument
  with "plan_id" argument linking to aws_backup_plan resource
  with "resources" argument including the aws_instance resource

