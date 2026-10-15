# Prompt 81

## Resources

aws_route53_health_check, aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Configure Active-Passive Failover policies using Route 53 resources. Name the health check resource "primary_health_check" and use a fqdn. Call the zone "primary"

## Difficulty

4

## Intent

Has one "aws_route53_zone" resource
    with "name"

Has two "aws_route53_record" resources
    The first "aws_route53_record" 
        with "name"
        with "type"
        with "ttl"
        with "records"
        with "zone_id" referencing the "aws_route53_zone" resource
        with "health_check_id" referencing the "aws_health_check" resource
        with "set_identifier"
        with "failover_routing_policy" block that contains "type" = "PRIMARY"
    The second "aws_route53_record"
        with "name"
        with "type"
        with "ttl"
        with "records"
        with "zone_id" referencing the "aws_route53_zone" resource
        with "set_identifier"
        with "failover_routing_policy" block that contains "type" = "SECONDARY"

Has one "aws_health_check" resources
    with "fqdn" 
    with "request_interval"
    with "type"



