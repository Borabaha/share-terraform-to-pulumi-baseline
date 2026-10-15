# Prompt 260

## Resources

aws_redshift_cluster, aws_redshift_event_subscription, aws_redshift_parameter_group, aws_sns_topic

## Prompt

Create an AWS Redshift cluster with an example AWS Redshift parameter group resource attached with an AWS Redshift event subscription resource that sends events associated with the parameter group to an AWS SNS topic.

## Difficulty

4

## Intent

Has one resource "aws_sns_topic"

Has one resource "aws_redshift_parameter_group"

Has one resource "aws_redshift_cluster"
with cluster_parameter_group_name = parameter group id

Has one resource "aws_redshift_event_subscription"
with source_type = "cluster-parameter-group"
and sns topic referenced in sns_topic_arn
and parameter group referenced in source_ids

