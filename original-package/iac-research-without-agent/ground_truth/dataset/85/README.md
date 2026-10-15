# Prompt 85

## Resources

aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Configure a routing policy that utilizes a user's location to route them to the nearest endpoint of a route 53 zone using Route 53 resources. Call the zone "primary" and use "US" and "EU" continents

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
        with "geolocation_routing_policy" block that contains "continent" set to "NA" 
    The second "aws_route53_record" 
        with "name"
        with "type"
        with "ttl"
        with "records"
        with "zone_id" referencing the "aws_route53_zone" resource
        with "set_identifier"
        with "geolocation_routing_policy" block that contains "continent" set to "EU" 


