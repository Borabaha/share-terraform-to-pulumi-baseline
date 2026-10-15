# Prompt 333

## Resources

aws_db_instance, aws_db_parameter_group, aws_db_subnet_group, aws_kms_key, aws_security_group, aws_subnet, aws_subnet

## Prompt

Provision a secure PostgreSQL database instance within a specified AWS VPC, leveraging AWS services like RDS, subnets, and KMS for encryption. It sets up a custom parameter group for PostgreSQL settings, and a security group to manage access. The database instance is configured with specifications like storage size, engine version, multi-AZ deployment for high availability, and encryption using a KMS key. The database instance is configured with "pgsnapshot" as final snopshot identifier.

## Difficulty

6

## Intent

Has one "aws_db_instance" resource
with one "allocated_storage" = 200
with one "engine" = "postgres"
with one "instance_class" and a valid instance class type, such as "db.t3.micro"
with one "password"
with one "username"
with "storage_encrypted" = true
with one final_snapshot_identifier       = "pgsnapshot"

Has one "aws_security_group" resource
with rules to manage access to the PostgreSQL database instance

Has one "aws_db_subnet_group" resource
with "subnet_ids" including at least two subnets within the VPC

Has one "aws_db_parameter_group" resource
with customized parameters for PostgreSQL settings, such as "password_encryption" and "rds.force_ssl"

Has one "aws_kms_key" resource
for encrypting the PostgreSQL database storage

