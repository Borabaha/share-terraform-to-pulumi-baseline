# Prompt 433

## Resources

aws_internet_gateway, aws_vpc

## Prompt

creates a VPC with a CIDR block of 10.0.0.0/16 and an internet gateway in the AWS us-east-2 region, both tagged with names "vpc" and "ig" respectively.

## Difficulty

3

## Intent

Has one "aws_vpc" resource:
with a specified "cidr_block" of "10.0.0.0/16"
with "enable_dns_hostnames" set to true
with a "tags" map that is not null, including at least a "Name" key with a value

Has one "aws_internet_gateway" resource:
with "vpc_id" referencing the "aws_vpc" resource by its ID
with a "tags" map that is not null, including at least a "Name" key with a value

