# Prompt 253

## Resources

aws_chime_voice_connector, aws_chime_voice_connector_streaming

## Prompt

Create an AWS Chime Voice Connector with encryption. Then configure the streaming of the voice connector with retention period of 5 hours, notifications sent to SNS, and disable streaming to Amazon Kinesis.

## Difficulty

2

## Intent

Has one resource "aws_chime_voice_connector"
with require_encryption=true

Has one resource "aws_chime_voice_connector_streaming"
with voice_connector_id equal to the id of the voice connector
with streaming_enabled = false
with data_retention = 5
streaming_notification_targets = ["SNS"]

