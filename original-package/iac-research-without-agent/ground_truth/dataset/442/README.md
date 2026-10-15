# Prompt 442

## Resources

aws_vpc_dhcp_options, aws_vpc_dhcp_options_association

## Prompt

creates DHCP options named "pike" for an AWS VPC, specifying Google's DNS servers (8.8.8.8 and 8.8.4.4), and then associates these DHCP options with a specified VPC, tagging both the DHCP options and their association with "permissions".

## Difficulty

3

## Intent

Has one "aws_vpc_dhcp_options" resource:
Specifies Google's DNS servers (8.8.8.8 and 8.8.4.4) as the DNS servers for the DHCP options
Tagged with "permissions" to categorize or specify its role or access levels within the infrastructure

Has one 
"aws_vpc_dhcp_options_association" resource:
Associates the "aws_vpc_dhcp_options" with a specified "aws_vpc" resource
Tagged with "permissions" to ensure consistent labeling and access management across related resources

