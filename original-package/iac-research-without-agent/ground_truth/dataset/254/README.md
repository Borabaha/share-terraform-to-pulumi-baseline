# Prompt 254

## Resources

aws_chime_voice_connector, aws_chime_voice_connector_streaming

## Prompt

Create an AWS Chime Voice Connector. Then set up a configuration to stream media to Amazon Kinesis.

## Difficulty

2

## Intent

Has one resource "aws_chime_voice_connector"

Has one resource "aws_chime_voice_connector_streaming"
with voice_connector_id equal to the id of the voice connector
with data_retention to some number

