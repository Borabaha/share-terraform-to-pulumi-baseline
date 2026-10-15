# Prompt 79

## Resources

aws_route53_record, aws_route53_zone

## Prompt

Set up a non-alias aws_route_53 record that is linked to an aws_route53_zone resource named "example53.com"

## Difficulty

2

## Intent

Has one "aws_route53_zone" resource
    with "name" set to "example53.com"

Has one "aws_route53_record" resource
    with "name"
    with "type"
    with "ttl"
    with "records"
    with "zone_id" referencing the "aws_route53_zone" resource


