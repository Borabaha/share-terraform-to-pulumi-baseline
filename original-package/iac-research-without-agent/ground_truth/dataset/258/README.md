# Prompt 258

## Resources

aws_redshift_cluster, aws_redshift_event_subscription, aws_sns_topic

## Prompt

Create an AWS Redshift cluster with an AWS Redshift event subscription resource that sends events to an AWS SNS topic

## Difficulty

3

## Intent

Has one resource "aws_sns_topic"

Has one resource "aws_redshift_cluster"

Has one resource "aws_redshift_event_subscription"
with source_type = "cluster"
and sns topic referenced in sns_topic_arn
and cluster referenced in source_ids

