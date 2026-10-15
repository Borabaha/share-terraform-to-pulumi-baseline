package main

import rego.v1

default allow := false

allow if {
    public_subnet_exists
    private_subnet_exists
    aws_instances
    rds_exist
}

public_subnet_exists if {
    some resource in input.resource_changes
    resource.type == "aws_subnet"
    resource.change.after.map_public_ip_on_launch == true
}

private_subnet_exists if {
    some resource in input.resource_changes
    resource.type == "aws_subnet"
    resource.change.after.map_public_ip_on_launch == false
}

aws_instances if {
    count([resource | resource := input.resource_changes[_]; resource.type == "aws_instance"]) == 2
}

rds_exist if {
    some resource in input.resource_changes
    resource.type == "aws_db_instance"
}
