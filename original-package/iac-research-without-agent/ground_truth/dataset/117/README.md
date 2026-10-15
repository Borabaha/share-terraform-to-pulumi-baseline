# Prompt 117

## Resources

aws_s3_bucket, aws_s3_bucket_notification, aws_sns_topic, aws_iam_policy_document

## Prompt

Create an IAM policy document that allows the 's3.amazonaws.com' service to publish to an SNS topic for S3 event notifications. Specify the actions as 'SNS:Publish' and set the resource to the ARN of the SNS topic 's3-event-notification-topic'. Apply a condition to allow this action only if the source ARN is similar to the ARN of the specified S3 bucket. Create an SNS topic named 's3-event-notification-topic' with the generated IAM policy. Set up an S3 bucket named 'your-bucket-name' and configure it to send notifications to the SNS topic for 's3:ObjectCreated:*' events with a filter for '.log' suffix.

## Difficulty

3

## Intent

Data "aws_iam_policy_document"
has one "effect"
has one "principals" 
has one "actions"
has one "resources"

Resource "aws_sns_topic" 
has one "name"
uses the JSON output

Resource "aws_s3_bucket" 
has one "bucket"

Resource "aws_s3_bucket_notification" 
has one "bucket"
configures a "topic" notification with:
"topic_arn"
"events"
"filter_suffix"

