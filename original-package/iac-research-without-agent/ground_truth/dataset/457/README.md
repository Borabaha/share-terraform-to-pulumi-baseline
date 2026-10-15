# Prompt 457

## Resources

aws_network_acl, aws_vpc

## Prompt

configures AWS as the cloud provider. It defines an AWS VPC with a specific CIDR block of 10.0.0.0/16 and a network ACL linked to this VPC that allows specific TCP traffic for both ingress and egress rules.

## Difficulty

3

## Intent

Has one "aws_vpc" resource:
with a specified "cidr_block" of "10.0.0.0/16"

Has one "aws_network_acl" resource:
linked to the "aws_vpc" resource
with ingress rules allowing TCP traffic
with egress rules allowing TCP traffic

