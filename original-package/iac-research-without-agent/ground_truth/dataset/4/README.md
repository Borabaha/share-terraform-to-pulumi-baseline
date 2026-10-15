# Prompt 4

## Resources

aws_db_instance, aws_db_instance, aws_db_subnet_group, aws_route53_record, aws_route53_record, aws_route53_zone, aws_route53_zone, aws_subnet, aws_subnet, aws_vpc

## Prompt

Configure Route 53 to return different database endpoints to internal versus external users. Internal users are routed to an internal RDS instance, while external users are routed to a publicly accessible one. Name the zones "private" and "public", the databases "internal" and "public", and the subnet group "main"

## Difficulty

6

## Intent

Has one "aws_vpc" resource
    with a specified "cidr_block"

Has multiple "aws_subnet" resources
    with "vpc_id" referencing the "aws_vpc" resource
    with specified "cidr_block" for each
    with "availability_zone" set

Has one "aws_db_subnet_group" resource
    with "subnet_ids" referencing the IDs of "aws_subnet" resources

Has one "aws_route53_zone" resource
    with "name"

Has one "aws_route53_zone" resource
    with "name"
    with a "vpc" block with "vpc_id" referencing the "aws_vpc" resource


Has one "aws_db_instance" resource for internal use
    with "allocated_storage" set to a specific size
    with a specified "engine" 
    with a specified "instance_class"
    with "username" and "password"
    with "skip_final_snapshot" set to true
    with "identifier"
    with "password"
    with "db_subnet_group_name" referencing the "aws_db_subnet_group" resource

Has one "aws_db_instance" resource for public use
    with "allocated_storage" set to a specific size
    with a specified "engine"
    with a specified "instance_class"
    with "username" and "password"
    with "skip_final_snapshot" set to true
    with "identifier"
    with "password"
    with "publicly_accessible" set to true

Has two "aws_route53_record" resources
    with "zone_id" referencing one of the "aws_route53_zone" resources
    with "type"
    with "ttl"
    with "records" referencing one of the "aws_db_instance" resources 


