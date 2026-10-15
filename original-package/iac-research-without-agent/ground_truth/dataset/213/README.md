# Prompt 213

## Resources

aws_iam_role, aws_msk_cluster, aws_mskconnect_connector, aws_mskconnect_custom_plugin, aws_s3_bucket, aws_s3_object, aws_security_group, aws_subnet, aws_subnet, aws_subnet, aws_vpc, aws_availability_zones

## Prompt

Create a managed MSK with 3 broker nodes in us-east-1. Creates an MSK Connect custom plugin using a "debezium.zip" and finally create an MSK Connect connector that uses the custom plugin and connects to the MSK cluster

## Difficulty

6

## Intent

Has one "aws_mskconnect_custom_plugin" resource
with one "content_type" = "ZIP"
with one "location"
with one "s3"
with one "file_key" = "debezium.zip"
Has one "aws_mskconnect_connector" resource

