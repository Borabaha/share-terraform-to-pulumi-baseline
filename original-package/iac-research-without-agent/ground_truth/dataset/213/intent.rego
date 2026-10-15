package main

import rego.v1

default allow := false
default msk_connect_plugin_created := false
default plugin_content_type_valid := false
default plugin_name_valid := false
default msk_connect_connector_created := false
default connector_uses_custom_plugin := false

# Check if an MSK Connect Custom Plugin is created
msk_connect_plugin_created if {
    some resource in input.resource_changes
    resource.type == "aws_mskconnect_custom_plugin"
    resource.change.actions[_] == "create"
}

# Check if the custom plugin uses a ZIP file
plugin_content_type_valid if {
    some resource in input.resource_changes
    resource.type == "aws_mskconnect_custom_plugin"
    resource.change.after.content_type == "ZIP"
}

# Check for the custom plugin name
plugin_name_valid if {
    some resource in input.resource_changes
    resource.type == "aws_mskconnect_custom_plugin"
    resource.change.after.location[0].s3[0].file_key == "my-connector.zip"
}

# Check if an MSK Connect Connector is created
msk_connect_connector_created if {
    some resource in input.resource_changes
    resource.type == "aws_mskconnect_connector"
    resource.change.actions[_] == "create"
}

# Check if the connector uses the custom plugin
connector_uses_custom_plugin if {
    some resource in input.resource_changes
    resource.type == "aws_mskconnect_connector"
    some plugin in input.resource_changes
    plugin.type == "aws_mskconnect_custom_plugin"
}

# Allow condition
allow if {
    msk_connect_plugin_created
    plugin_content_type_valid
    plugin_name_valid
    msk_connect_connector_created
    connector_uses_custom_plugin
}
