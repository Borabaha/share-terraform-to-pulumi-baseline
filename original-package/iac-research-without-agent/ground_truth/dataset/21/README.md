# Prompt 21

## Resources

aws_route53_record, aws_route53_zone

## Prompt

Set up a record that maps a domain name to an IPv6 address using Route 53 resources

## Difficulty

2

## Intent

Has one "aws_route53_zone" resource
    with "name" set to "example53.com"

Has one "aws_route53_record" resource
    with "name"
    with "type" set to "AAAA"
    with "ttl"
    with "records"
    with "zone_id" referencing the "aws_route53_zone" resource


