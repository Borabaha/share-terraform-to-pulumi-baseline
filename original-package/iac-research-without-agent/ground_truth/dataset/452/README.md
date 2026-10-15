# Prompt 452

## Resources

aws_vpc, aws_vpc, aws_vpc_peering_connection

## Prompt

establishes a VPC peering connection between two AWS Virtual Private Clouds (VPCs). The first VPC, named "peer," is configured with a CIDR block of 10.0.0.0/24, and the second VPC, named "base," has a CIDR block of 10.1.0.0/24. The peering connection, named "pike," connects these two VPCs, allowing them to communicate with each other as if they were in the same network, and is tagged with pike = "permissions" to indicate its purpose or management policy.

## Difficulty

3

## Intent

Has two "aws_vpc" resources:
The first VPC is named "peer" and is configured with a "cidr_block" of "10.0.0.0/24".
The second VPC is named "base" and is configured with a "cidr_block" of "10.1.0.0/24".

Has one "aws_vpc_peering_connection" resource:
Named "pike" to connect the two specified VPCs ("peer" and "base").
Configured to allow the VPCs to communicate with each other as if they were in the same network.
Tagged with "pike" set to "permissions", indicating its purpose or management policy within the infrastructure.

