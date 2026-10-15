# Prompt 3

## Resources

aws_db_instance, aws_db_instance, aws_db_instance, aws_db_instance, aws_route53_record, aws_route53_record, aws_route53_record, aws_route53_zone

## Prompt

Using route 53 resources, configure a weighted routing policy that splits users between three db_instances that are replicas of a main db_instance. Provision the three replica instances in "us-east-1", "eu-central-1", and "ap-southeast-1". Provision the zone and main db_instance in "us-west-1". Call the zone "main", the original db_instance "primary", the three replicas "replica_us_east", "replica_eu_central" and "replica_ap_southeast" respectively, and the provider aliases "main", "us-east", "eu-central", and "ap-southeast".

## Difficulty

6

## Intent

Has one "aws_route53_zone" resource
    with "name"

Has a "aws_db_instance" resource
    with "identifier" set to "master"
    with "instance_class"
    with "allocated_storage"
    with "engine"
    with "username"
    with "password"
    with "backup_retention_period" set to a non-zero number

Has multiple "aws_db_instance" resources
    with "identifier"
    with "replicate_source_db" referencing the main "aws_db_instance" resource
    with "instance_class"

Has multiple "aws_route53_record" resources
    with "name"
    with "type"
    with "ttl"
    with "zone_id" referencing the "aws_route53_zone" resource
    with "weighted_routing_policy" block that contains "weight" as a non-zero number
    with "records" containing an endpoint of a corresponding replica of the main "aws_db_instance"



