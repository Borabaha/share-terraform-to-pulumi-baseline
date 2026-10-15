package aws_chime_voice_connector

import rego.v1

default valid := false

valid if {
	some vc in input.configuration.root_module.resources
	vc.type == "aws_chime_voice_connector"

	some vc_logging in input.configuration.root_module.resources
	vc_logging.type = "aws_chime_voice_connector_logging"
	vc_logging.expressions.enable_sip_logs.constant_value == false
	vc_logging.expressions.enable_media_metric_logs.constant_value == true
	vc.address in vc_logging.expressions.voice_connector_id.references
}
