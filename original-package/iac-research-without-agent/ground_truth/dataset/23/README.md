# Prompt 23

## Resources

aws_route53_record, aws_route53_zone

## Prompt

Set up a TXT recordfor domain ownership verification purposes using Route 53 resources. The verification string should be "passwordpassword" and the name of the zone should be "example"

## Difficulty

2

## Intent

Has one "aws_route53_zone" resource
    with "name" set to "example53.com"

Has one "aws_route53_record" resource
    with "name"
    with "type" set to "TXT"
    with "ttl"
    with "records" set to a string
    with "zone_id" referencing the "aws_route53_zone" resource


