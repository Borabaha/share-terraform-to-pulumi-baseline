# Prompt 235

## Resources

aws_egress_only_internet_gateway, aws_vpc

## Prompt

Create an AWS VPC with an Egress-Only Internet Gateway attached to it

## Difficulty

2

## Intent

Has one resource "aws_vpc"

Has one resource "aws_egress_only_internet_gateway"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

