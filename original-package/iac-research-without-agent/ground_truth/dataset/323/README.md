# Prompt 323

## Resources

aws_instance, aws_key_pair, aws_lb, aws_lb_listener, aws_lb_target_group, aws_lb_target_group_attachment, aws_route53_record, aws_route53_record, aws_route53_zone, aws_s3_bucket, aws_security_group, aws_subnet, aws_subnet, aws_vpc, aws_vpc_security_group_egress_rule, aws_vpc_security_group_ingress_rule, aws_ami

## Prompt

An AWS VPC module with cidr of value "10.0.0.0/16". Three AWS subnets linking to the VPC with with cidr_block "10.0.4.0/24", "10.0.5.0/24" and "10.0.6.0/24". An AWS security group linking to the VPC. One AWS security group ingress rule and one egress rul to allow ingress from the VPC ip range and from port 80 to port 80 with protocol tcp and egress from any ip and from port 80 to port 80 with protocol tcp.
An AWS Load Balancing resource with a load_balancer_type argument "application", a security_groups argument linking to a security group resource, and a subnets argument with linking to the three AWS VPC subnest. An AWS LB target group linking to the same AWS VPC resource as AWS LB and has a port argument with value 80 and a protocol argument with value "HTTP". An AWS LB listener linking to the LB resource and the LB target group with type "forward". An AWS LB terget group attachment resource to attach an AWS EC2 instance with latest ubuntu environment to the LB target group resource. An AWS Route53 zone with name argument of value "test-video-stream.com". Two AWS Route53 alias records for "lb.test-video-stream.com" to be linked to the LB resource DNS and the domain name "test-video-stream.com" for both IPv4 and IPv6 with evaluate_target_health argument as true.

## Difficulty

6

## Intent

have one "aws_s3_bucket" resource
  with "bucket" argument with value "video-content-bucket"
have one "aws_lb" resource
  with "subnets" argument linking to aws_subnet resources
  with "security_groups" argument linking aws_security_group resource
have one "aws_lb_listener" resource
  with "load_balancer_arn" argument linking to the aws_lb resource
  with "port" argument set to 443
  with "protocol" argument with value "HTTPS"
  with "default_action" argument block
    with "type" argument with value "forward"
    with "target_group_arn" argument linking to aws_lb_target_group resource
with one "aws_lb_target_group" resource
  with "name" argument
  with "port" argument set to 443
  with "protocol" argument with value "HTTPS"
  with "vpc_id" argument linking to the aws_vpc resource
with one "aws_lb_target_group_attachment" resource
  with "target_group_arn" argument linking to the aws_lb_target_group resource
  with "target_id" argument linking to the aws_instance resource
  with "port" set to 443
have one "aws_ami" resource
  with "filter" argument block
    with "name" argument
    with "values" argument with value "al2023-ami-2023.*-x86_64"
have one "aws_key_pair" resource
  with "public_key" argument
have one "aws_instance" resource
  with "ami" argument linking to ami resource
  with "instance_type" argument with value "t2.micro"
  with "key_name" argument linking to key_pair resource
have one "aws_vpc" resource
  with "cidr_block" argument with value "10.0.0.0/16"
have two "aws_subnet" resources
  with "vpc_id" argument linking to the aws_vpc resource
  with "cidr_block" argument with values "10.0.1.0/24" and "10.0.2.0/24"
have one "aws_security_group" resource
  with "vpc_id" argument linking to the aws_vpc resource
have one "aws_vpc_security_group_ingress_rule" resource
  with "security_group_id" argument linking to the aws_security_group resource
  with "cidr_ipv4" argument with cidr_block of the aws_vpc resource
  with "from_port" argument set to 443
  with "to_port" argument set to 443
  with "ip_protocol" argument with value "tcp"
have one "aws_vpc_security_group_egress_rule" resource
  with "security_group_id" argument linking to the aws_security_group resource
  with "cidr_ipv4" argument with value "0.0.0.0/0"
  with "from_port" argument set to 443
  with "to_port" argument set to 443
  with "ip_protocol" argument with value "tcp"
have one "aws_route53_zone" resource
  with "name" argument with value "netflix.com"
have two "aws_route53_record" resources
  with "type" argument with values "A" and "AAAA"
  with "name" argument with value "lb"
  with "zone_id" argument linking to the aws_route53_zone resource
  with "alias" argument block
    with "name" argument linking to the aws_lb dns_name
    with "zone_id" argument linking to aws_lb zone_id
    with "evaluate_target_health" argument set to true

