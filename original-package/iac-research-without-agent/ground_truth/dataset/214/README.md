# Prompt 214

## Resources

aws_cloudwatch_log_group, aws_iam_role, aws_iam_role, aws_kinesis_firehose_delivery_stream, aws_kms_key, aws_msk_cluster, aws_mskconnect_connector, aws_mskconnect_custom_plugin, aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_ownership_controls, aws_s3_object, aws_security_group, aws_subnet, aws_subnet, aws_subnet, aws_vpc, aws_availability_zones, aws_iam_policy_document

## Prompt

Create a MSK with 3 broker nodes outputting to a CloudWatch log group, an S3 bucket, a Kinesis Firehose delivery stream. The MSK should encryption at rest, open monitoring. Creates an MSK Connect custom plugin using a "debezium.zip" and finally create an MSK Connect connector that uses the custom plugin and connects to the MSK cluster

## Difficulty

6

## Intent

Has one "aws_msk_cluster" resource
with one "number_of_broker_nodes" = 3
with one "logging_info"
with one "broker_logs"
with one "cloudwatch_logs"
with one "enabled" = true
with one "s3"
with one "enabled" = true
with one "firehose"
with one "enabled" = true
with one "encryption_info"
with one "encryption_at_rest_kms_key_arn"
with one "open_monitoring"
with one "prometheus"
with one "jmx_exporter"
with one "enabled_in_broker" = true
with one "node_exporter"
with one "enabled_in_broker" = true
# Requires aws provider with alias of "aws" with a region of us-east-1
Has one "aws_mskconnect_custom_plugin" resource
with one "content_type" = "ZIP"
Has one "aws_mskconnect_connector" resource

