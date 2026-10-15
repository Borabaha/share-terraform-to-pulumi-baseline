# Prompt 445

## Resources

aws_vpc, aws_vpc_dhcp_options, aws_vpc_dhcp_options_association

## Prompt

sets up a basic AWS network infrastructure consisting of a Virtual Private Cloud (VPC) with a custom DHCP options set. The VPC is configured with a CIDR block of 192.168.0.0/16. The DHCP options include a domain name (windomain.local), a combination of custom and Google's DNS servers (192.168.56.102 and 8.8.8.8), and a NetBIOS name server (192.168.56.102). These DHCP options are then associated with the created VPC, customizing its DHCP settings.








## Difficulty

3

## Intent

Has one "aws_vpc" resource:
Configured with a "cidr_block" of "192.168.0.0/16"
Includes associated custom DHCP options

Has one "aws_vpc_dhcp_options" resource:
Specifies a "domain_name" of "windomain.local"
Includes DNS servers with a combination of a custom DNS server ("192.168.56.102") and Google's DNS server ("8.8.8.8")
Configures a "NetBIOS" name server at "192.168.56.102"

Has one "aws_vpc_dhcp_options_association" resource:
Associates the "aws_vpc_dhcp_options" with the created "aws_vpc"
Customizes DHCP settings specifically for the created VPC environment

