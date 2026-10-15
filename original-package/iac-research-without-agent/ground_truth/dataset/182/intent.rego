package main

import rego.v1

default allow := false

aws_sagemaker_human_task_ui_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_human_task_ui"
	resource.change.after.ui_template[0].content == "\u003ch1\u003eTEST\u003c/h1\u003e\n"
}

# Aggregate all checks
allow if {
	aws_sagemaker_human_task_ui_valid(input.resource_changes)
}
