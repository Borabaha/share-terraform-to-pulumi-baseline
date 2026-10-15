# Prompt 390

## Resources

aws_instance, aws_lb, aws_lb_listener, aws_lb_target_group, aws_lb_target_group_attachment, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

generate an Application Load Balancer with name test-lb-tf, security groups, and subnets. it should not be internal, and enable deletion protection

## Difficulty

6

## Intent

has one "aws_lb" resource
    with name = test-lb-tf
    with internal = false
    with security_groups argument
    with enable_deletion-protection = true
    with load_balancer_type = application        
    with one of either "subnets" or "subnet_mapping"

has at least two aws_subnet
    has one of cidr_block, ipv6_cidr_block argument

has one aws_vpc
    has one of cider_block, ipv4_ipam_pool_id 


has one "aws_lb_listener" resource
    with one default_action argument
        with one type argument
            with one of following values: forward, redirect, fixed-response, authenticate-cognito and authenticate-oidc
    with one load_balancer_arn argument

has one "aws_lb_target_group"
    with port
    with protocol
    with vpc_id

has one aws_lb_target_group_attachment
    with one target_group_arn
    with one target_id

has at least one "aws_instance"
    with either launch_template or (ami and instance_type) argument

has one "aws_security_group"

