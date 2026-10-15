# Prompt 84

## Resources

aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Configure a routing policy that navigates users to the least congested endpoint of a route 53 zone using Route 53 resources. Call the zone "primary" and use "us-east-1" and "eu-central-1" regions

## Difficulty

3

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
        with "set_identifier"
        with "latency_routing_policy" block that contains "region" set to "us-east-1" 
    The second "aws_route53_record" 
        with "name"
        with "type"
        with "ttl"
        with "records"
        with "zone_id" referencing the "aws_route53_zone" resource
        with "set_identifier"
        with "latency_routing_policy" block that contains "region" set to "eu-central-1" 


