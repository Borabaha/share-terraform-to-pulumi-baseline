# Prompt 83

## Resources

aws_cloudwatch_metric_alarm, aws_route53_health_check

## Prompt

Configure a health check with route 53 that uses a cloudwatch metric alarm called "foobar". Set the metric_name to "CPUUtilization", namespace to "AWS/EC2", statistic to "Average", period to "120", and comparison_operator to "GreaterThanOrEqualToThreshold". If the health check doesn't have enough info about the alarm, the status should be "Healthy". All resources should be provisioned in "us-east-1"

## Difficulty

3

## Intent

Has one "aws_cloudwatch_metric_alarm"" resources
    with "alarm_name"
    with "comparison_operator" set to "GreaterThanOrEqualToThreshold"
    with "evaluation_periods"
    with "namespace" set to "AWS/EC2"
    with "period" set to "120"
    with "statistic" set to "Average"
    with "metric_name" set to "CPUUtilization"
    with "threshold"

Has one "aws_route53_health_check" resources
    with "cloudwatch_alarm_name" referencing the "aws_cloudwatch_metric_alarm" resource
    with "cloudwatch_alarm_region" 
    with "insufficient_data_health_status" set to "Healthy"
    with "type" equal to "CLOUDWATCH"



