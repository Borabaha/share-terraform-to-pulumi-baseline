# Prompt 249

## Resources

aws_chime_voice_connector, aws_chime_voice_connector, aws_chime_voice_connector_group

## Prompt

Create two AWS Chime Voice Connectors, both with encryption. Then create an aws_chime_voice_connector_group resource with both of these connectors. One connector should be prioritized over the other.

## Difficulty

3

## Intent

Has one resource "aws_chime_voice_connector"
with require_encryption="true"

Has another resource "aws_chime_voice_connector"
with require_encryption="true"

Has one resource "aws_chime_voice_connector_group"
with a connector for each voice connector with the correct id
one connector should have a priority higher than the other

