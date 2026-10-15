package main

import rego.v1

default allow := false

# Check if any MSK cluster is being created
msk_cluster_created(resources) if {
	some resource in resources
	resource.type == "aws_msk_cluster"
	resource.change.actions[_] == "create"
}

# Check if both jmx_exporter and node_exporter are enabled
prometheus_exporters_enabled(resource) if {
	resource.type == "aws_msk_cluster"
	resource.change.after.open_monitoring[_].prometheus[_].jmx_exporter[_].enabled_in_broker == true
	resource.change.after.open_monitoring[_].prometheus[_].node_exporter[_].enabled_in_broker == true
}

# Aggregate all checks
allow if {
	msk_cluster_created(input.resource_changes)
	some resource in input.resource_changes
	prometheus_exporters_enabled(resource)
}
