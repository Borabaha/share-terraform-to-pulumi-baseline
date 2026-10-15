package main

import rego.v1

default allow := false
default aws_instance_count := 0
default subnet_a_exists := false
default subnet_b_exists := false
default ami_valid := false
default instance_type_valid := false
default root_block_device_valid := false

aws_instance_count := count([resource | 
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_ami(resource)
    check_instance_type(resource)
    check_root_block_device(resource)
])

subnet_a_exists if {
    some resource in input.resource_changes
    resource.type == "aws_subnet"
    resource.change.after.availability_zone == "us-east-1a"
    resource.change.after.cidr_block == "10.0.1.0/24"
}

subnet_b_exists if {
    some resource in input.resource_changes
    resource.type == "aws_subnet"
    resource.change.after.availability_zone == "us-east-1b"
    resource.change.after.cidr_block == "10.0.2.0/24"
}

ami_valid if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_ami(resource)
}

instance_type_valid if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_instance_type(resource)
}

root_block_device_valid if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_root_block_device(resource)
}

allow if {
    aws_instance_count == 2
    subnet_a_exists
    subnet_b_exists
    ami_valid
    instance_type_valid
    root_block_device_valid
}

check_ami(aws_instance) if {
    aws_instance.change.after.ami == "ami-04681a1dbd79675a5"
}

check_instance_type(aws_instance) if {
    aws_instance.change.after.instance_type == "t2.micro"
}

check_root_block_device(aws_instance) if {
    aws_instance.change.after.root_block_device[0].volume_size == 50
}
