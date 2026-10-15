# Prompt 259

## Resources

aws_redshift_cluster, aws_redshift_event_subscription, aws_redshift_parameter_group, aws_sns_topic

## Prompt

Create an AWS Redshift cluster with example cluster parameters and notifications on events associated with the parameter group

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

