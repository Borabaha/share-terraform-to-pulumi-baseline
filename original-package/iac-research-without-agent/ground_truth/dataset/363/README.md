# Prompt 363

## Resources

aws_lightsail_instance, aws_lightsail_static_ip, aws_lightsail_static_ip_attachment

## Prompt

create Amazon Lightsail with static ipv4 IP

## Difficulty

2

## Intent

have one "aws_lightsail_instance" resource
    with "name" argument
    with "availability_zone" argument
    with "blueprint_id" argument
    with "bundle_id" argument

has one "aws_lightsail_static_ip" resource
    with "name" argument

has one "aws_lightsail_static_ip_attachment" resource
    with "static_ip_name" argument
    with "instance_name" argument

