# Prompt 246

## Resources

aws_chime_voice_connector, aws_chime_voice_connector, aws_chime_voice_connector_group

## Prompt

Create two AWS Chime Voice Connectors, both with encryption, and group these together

## Difficulty

3

## Intent

Has one resource "aws_chime_voice_connector"
with require_encryption="true"

Has another resource "aws_chime_voice_connector"
with require_encryption="true"

Has one resource "aws_chime_voice_connector_group"
with a connector for each voice connector with the correct id

