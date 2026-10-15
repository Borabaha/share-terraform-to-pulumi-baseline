# Prompt 22

## Resources

aws_route53_record, aws_route53_zone

## Prompt

Set up a Pointer record for reverse DNS using Route 53 resources. The domain name should be "host.example53.com" and name the zone "reverse_zone"

## Difficulty

2

## Intent

Has one "aws_route53_zone" resource
    with "name" ending in ".in-addr.arpa"

Has one "aws_route53_record" resource
    with "name"
    with "type" set to "PTR"
    with "ttl"
    with "records"
    with "zone_id" referencing the "aws_route53_zone" resource


