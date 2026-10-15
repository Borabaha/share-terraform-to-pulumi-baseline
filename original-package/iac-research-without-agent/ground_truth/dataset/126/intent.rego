package main

import rego.v1

default allow := false
default aws_instance_exists := false
default ami_valid := false
default cpu_options_valid := false

aws_instance_exists if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
}

ami_valid if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_ami(resource)
}

cpu_options_valid if {
    some resource in input.resource_changes
    resource.type == "aws_instance"
    check_cpu_options(resource)
}

allow if {
    aws_instance_exists
    ami_valid
    cpu_options_valid
}

check_ami(aws_instance) if {
    aws_instance.change.after.ami #== "ami-04681a1dbd79675a5"
}

check_cpu_options(aws_instance) if {
    aws_instance.change.after.cpu_options[_]["core_count"] == 2
    aws_instance.change.after.cpu_options[_]["threads_per_core"] == 2
}

check_cpu_options(aws_instance) if {
    aws_instance.change.after.cpu_core_count == 2
    aws_instance.change.after.cpu_threads_per_core == 2
}