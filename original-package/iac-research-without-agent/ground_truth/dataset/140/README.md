# Prompt 140

## Resources

aws_redshift_cluster, aws_redshift_usage_limit

## Prompt

Create a 2 node RedShift cluster and limit the concurrency scaling to 60 minutes

## Difficulty

2

## Intent

Has an aws_redshift_cluster resource and check cluster_type is "single_node" or number of nodes is 2, check there is a aws_redshift_usage_limit resouce where the feature type is concurrency_scaling, limit_type is "time", and amount is 60

