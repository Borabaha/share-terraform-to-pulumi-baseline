# Prompt 239

## Resources

aws_internet_gateway, aws_route_table, aws_vpc

## Prompt

Create an AWS VPC resource with an Internet Gateway attached and a route to a custom route table directing traffic for a specific CIDR block through the Internet Gateway

## Difficulty

2

## Intent

Has one resource "aws_vpc"

Has one resource "aws_internet_gateway"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has one resource "aws_route_table"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"
with one route

