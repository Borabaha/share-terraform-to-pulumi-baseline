# Prompt 250

## Resources

aws_chime_voice_connector, aws_chime_voice_connector_logging

## Prompt

Create an AWS Chime Voice Connector. Then create an AWS Chime Voice Connector Logging resource with enable_sip_logs disabled and enable_media_metric_logs enabled

## Difficulty

2

## Intent

Has one resource "aws_chime_voice_connector"

Has one resource "aws_chime_voice_connector_logging"
with voice_connector_id equal to the id of the voice connector
with enable_sip_logs false
with enable_media_metric_logs true

