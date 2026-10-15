# Prompt 237

## Resources

aws_network_acl, aws_subnet, aws_vpc

## Prompt

Create an AWS VPC resource with a subnet and associated network ACLs to control both ingress and egress traffic

## Difficulty

3

## Intent

Has one resource "aws_vpc"

Has one resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has one resource "aws_network_acl"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"
with one "egress" with correct parameters
with one "ingress" with correct parameters

