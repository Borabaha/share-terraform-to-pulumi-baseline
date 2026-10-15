# Prompt 240

## Resources

aws_instance, aws_subnet, aws_vpc, aws_ami

## Prompt

Create an AWS VPC resource with one subnet and then launches an EC2 instance into that subnet. Use AMI lookup for an ubuntu 20.04 AMD64 server.

## Difficulty

3

## Intent

Has one resource "aws_vpc"

Has one resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has one data source "aws_ami"
with one "filter" with "values" = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"

Has one resource "aws_instance"
with one "ami" with value "data.aws_ami.{DATA NAME}.id"
with one "subnet_id" with value "aws_subnet.{SUBNET NAME}.id"

