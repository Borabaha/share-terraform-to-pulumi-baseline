# Prompt 450

## Resources

aws_nat_gateway

## Prompt

creates a NAT Gateway associated with a specified subnet and Elastic IP allocation ID. The NAT Gateway is configured for private connectivity and tagged with a key-value pair (pike = "permissions"), indicating its purpose or ownership.

## Difficulty

3

## Intent

Has one "aws_nat_gateway" resource:
Associated with a specified "aws_subnet" resource for hosting the NAT Gateway.
Utilizes an "Elastic IP allocation ID" to provide the NAT Gateway with a public IP address.
Configured for private connectivity, allowing resources within the private subnet to access the internet securely.
Tagged with a key-value pair: "pike" set to "permissions", which categorizes its role, purpose, or ownership within the infrastructure.

