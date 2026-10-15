package main

import rego.v1

default allow := false

allow if {
	check_aws_instance(input.resource_changes)
}

check_aws_instance(resources) if {
	some resource in resources
	resource.type == "aws_instance"
	check_ami(resource)
	check_cpu_options(resource)
}

check_ami(aws_instance) if {
	aws_instance.change.after.ami == "ami-04681a1dbd79675a5"
}

check_cpu_options(aws_instance) if {
    aws_instance.change.after.cpu_options[_]["core_count"] == 2
    aws_instance.change.after.cpu_options[_]["threads_per_core"] == 2
}

check_cpu_options(aws_instance) if {
    aws_instance.change.after.cpu_core_count == 2
    aws_instance.change.after.cpu_threads_per_core == 2
}

check_cpu_options(aws_instance) if {
	aws_instance.change.after.instance_type == "t3.2xlarge"
}