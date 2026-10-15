# Prompt 244

## Resources

aws_neptune_cluster, aws_neptune_cluster_instance, aws_neptune_cluster_parameter_group, aws_neptune_parameter_group

## Prompt

Set up a basic AWS Neptune cluster with a custom parameter group and an instance in that cluster with its own custom parameter group

## Difficulty

3

## Intent

Has "aws_neptune_cluster"
with "neptune_cluster_parameter_group_name"

Has "aws_neptune_cluster_parameter_group"
with family = "neptune1.2"

Has "aws_neptune_cluster_instance"
with "cluster_identifier"
with "neptune_parameter_group_name"
with "publicly_accessible" = false OR a subnet group defined

Has "aws_neptune_parameter_group"
with family = "neptune1.2"

