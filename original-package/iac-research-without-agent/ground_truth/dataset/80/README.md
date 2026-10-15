# Prompt 80

## Resources

aws_route53_record, aws_route53_zone, aws_vpc

## Prompt

Set up a non-alias aws_route_53 record that is linked to an aws_route53_zone resource called "private_zone" whose name paramter is set to "internal.example53.com" and has an aws_vpc resource called "main" attached to it

## Difficulty

3

## Intent

Has one "aws_vpc" resource
    with a specified "cidr_block"

Has one "aws_route53_zone" resource
    with "name" set to "internal.example53.com"
    with a "vpc" block that contains "vpc_id" that references the "aws_vpc" resource

Has one "aws_route53_record" resource
    with "name"
    with "type"
    with "ttl"
    with "records"
    with "zone_id" referencing the "aws_route53_zone" resource

