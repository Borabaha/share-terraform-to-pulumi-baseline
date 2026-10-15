# Prompt 234

## Resources

aws_internet_gateway, aws_vpc

## Prompt

Create an AWS VPC resource with an Internet Gateway attached to it

## Difficulty

2

## Intent

Has one resource "aws_vpc"

Has one resource "aws_internet_gateway"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

