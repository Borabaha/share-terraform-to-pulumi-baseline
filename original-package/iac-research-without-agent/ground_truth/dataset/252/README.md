# Prompt 252

## Resources

aws_chime_voice_connector, aws_chime_voice_connector_logging

## Prompt

Create an AWS Chime Voice Connector with encryption and log media metrics.

## Difficulty

2

## Intent

Has one resource "aws_chime_voice_connector"
with require_encryption=true

Has one resource "aws_chime_voice_connector_logging"
with voice_connector_id equal to the id of the voice connector
with enable_media_metric_logs true

