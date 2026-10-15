# Prompt 451

## Resources

aws_nat_gateway

## Prompt

creates a NAT Gateway associated with a specified subnet and Elastic IP allocation ID. The NAT Gateway is configured for public connectivity.

## Difficulty

2

## Intent

Has one "aws_nat_gateway" resource:
Associated with a specified "aws_subnet" resource for hosting the NAT Gateway.
Utilizes an "Elastic IP allocation ID" to provide the NAT Gateway with a public IP address.
Configured for public connectivity, allowing resources within the private subnet to access the internet securely.

