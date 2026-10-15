# Prompt 236

## Resources

aws_subnet, aws_subnet, aws_vpc

## Prompt

Create an AWS VPC resource with one public subnet and one private subnet

## Difficulty

2

## Intent

Has one resource "aws_vpc"

Has one resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has another resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

