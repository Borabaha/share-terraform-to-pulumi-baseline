package aws_neptune_cluster

import rego.v1

default valid := false
default vpc_exists := false
default subnet1_exists := false
default subnet2_exists := false
default subnet_group_valid := false
default neptune_cluster_exists := false
default cluster_parameter_group_valid := false

# Check if a VPC exists
vpc_exists if {
    some vpc in input.configuration.root_module.resources
    vpc.type == "aws_vpc"
}

# Check if at least one subnet exists in the VPC
subnet1_exists if {
    some subnet1 in input.configuration.root_module.resources
    some vpc in input.configuration.root_module.resources
    vpc.type == "aws_vpc"
    subnet1.type == "aws_subnet"
    vpc.address in subnet1.expressions.vpc_id.references
}

# Check if a second, distinct subnet exists in the VPC
subnet2_exists if {
    some subnet1 in input.configuration.root_module.resources
    some subnet2 in input.configuration.root_module.resources
    some vpc in input.configuration.root_module.resources
    vpc.type == "aws_vpc"
    subnet1.type == "aws_subnet"
    subnet2.type == "aws_subnet"
    vpc.address in subnet1.expressions.vpc_id.references
    vpc.address in subnet2.expressions.vpc_id.references
    not subnet1 == subnet2
}

# Check if a Neptune subnet group exists and includes both subnets
subnet_group_valid if {
    some subnet_group in input.configuration.root_module.resources
    some subnet1 in input.configuration.root_module.resources
    some subnet2 in input.configuration.root_module.resources
    subnet_group.type == "aws_neptune_subnet_group"
    subnet1.type == "aws_subnet"
    subnet2.type == "aws_subnet"
    subnet1.address in subnet_group.expressions.subnet_ids.references
    subnet2.address in subnet_group.expressions.subnet_ids.references
}

# Check if a Neptune cluster exists and references the subnet group
neptune_cluster_exists if {
    some cluster in input.configuration.root_module.resources
    some subnet_group in input.configuration.root_module.resources
    cluster.type == "aws_neptune_cluster"
    subnet_group.type == "aws_neptune_subnet_group"
    subnet_group.address in cluster.expressions.neptune_subnet_group_name.references
}

# Validate Neptune cluster parameter group
cluster_parameter_group_valid if {
    some cluster in input.configuration.root_module.resources
    some cluster_parameter_group in input.configuration.root_module.resources
    cluster.type == "aws_neptune_cluster"
    cluster_parameter_group.type == "aws_neptune_cluster_parameter_group"
    cluster_parameter_group.address in cluster.expressions.neptune_cluster_parameter_group_name.references


}

cluster_parameter_group_valid if {
    some cluster in input.configuration.root_module.resources
    some cluster_parameter_group in input.configuration.root_module.resources
    cluster.type == "aws_neptune_cluster"
    cluster_parameter_group.type == "aws_neptune_cluster_parameter_group"
    cluster_parameter_group.address in cluster.expressions.neptune_cluster_parameter_group_name.references


}

cluster_parameter_group_valid if {
    some cluster in input.configuration.root_module.resources
    some cluster_parameter_group in input.configuration.root_module.resources
    cluster.type == "aws_neptune_cluster"
    cluster_parameter_group.type == "aws_neptune_cluster_parameter_group"
    cluster_parameter_group.address in cluster.expressions.neptune_cluster_parameter_group_name.references

}

# Allow condition
valid if {
    vpc_exists
    subnet1_exists
    subnet2_exists
    subnet_group_valid
    neptune_cluster_exists
    cluster_parameter_group_valid
}
