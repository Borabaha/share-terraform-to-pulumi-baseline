package main

import rego.v1

default public_subnet_exists := false
default private_subnet_exists := false
default ec2_fleet_valid := false
default launch_template_valid := false

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

ec2_fleet_valid if {
	some resource in input.resource_changes
	resource.type == "aws_ec2_fleet"
	resource.change.after.launch_template_config[0].launch_template_specification[0].version == "$Latest"
	resource.change.after.target_capacity_specification[0].on_demand_target_capacity == 5
	resource.change.after.target_capacity_specification[0].spot_target_capacity == 4
}

launch_template_valid if {
	some resource in input.resource_changes
	resource.type == "aws_launch_template"
	resource.change.after.image_id == "ami-0591e1c6a24d08458"
}

allow if {
	public_subnet_exists
	private_subnet_exists
	ec2_fleet_valid
	launch_template_valid
}
