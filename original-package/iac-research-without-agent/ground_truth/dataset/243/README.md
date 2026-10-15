# Prompt 243

## Resources

aws_neptune_cluster, aws_neptune_cluster_parameter_group, aws_neptune_subnet_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Set up a basic AWS Neptune cluster with a custom parameter group that only allows connection from two example subnets

## Difficulty

4

## Intent

Has "aws_vpc"

Has two "aws_subnet"

Has "aws_neptune_subnet_group"
with subnet_ids = array with both "aws_subnet"

Has "aws_neptune_cluster"
with "neptune_cluster_parameter_group_name"
with "neptune_cluster_subnet_group"

Has "aws_neptune_cluster_parameter_group"
with family = "neptune1.2"

