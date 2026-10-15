# Prompt 245

## Resources

aws_neptune_cluster, aws_neptune_cluster_instance, aws_neptune_cluster_parameter_group, aws_neptune_parameter_group, aws_neptune_subnet_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Set up a basic AWS Neptune cluster with a custom parameter group and an instance in that cluster with its own custom parameter group. Only allow connections to the instance from an example subnet.

## Difficulty

5

## Intent

Has "aws_neptune_cluster"
with "neptune_cluster_parameter_group_name"
with "neptune_cluster_subnet_group" same as instance

Has "aws_neptune_cluster_parameter_group"
with family = "neptune1.2"

Has "aws_neptune_cluster_instance"
with "cluster_identifier"
with "neptune_parameter_group_name"
with "neptune_cluster_subnet_group" same as cluster

Has "aws_neptune_parameter_group"
with family = "neptune1.2"

Has "aws_vpc"

Has "aws_subnet"

Has "aws_neptune_subnet_group"
with subnet_ids = array with "aws_subnet" id

