# Prompt 388

## Resources

aws_instance, aws_lb, aws_lb_listener, aws_lb_target_group, aws_lb_target_group_attachment, aws_subnet, aws_vpc

## Prompt

Write a Terraform script to establish a Network Load Balancer attached to an ec2 instance of t2.micro

## Difficulty

4

## Intent

has one "aws_lb" resource
    with load_balancer_type = "network"

has one "aws_lb_listener" resource
    with one default_action argument
        with one type argument
            with one of following values: forward, redirect, fixed-response, authenticate-cognito and authenticate-oidc
    with one load_balancer_arn argument

has one aws_lb_target_group_attachment
    with one target_group_arn
    with one target_id

has one "aws_lb_target_group"

has at least one "aws_instance"
    with either launch_template or (ami and instance_type) argument

