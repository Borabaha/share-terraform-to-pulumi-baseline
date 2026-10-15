# Prompt 283

## Resources

aws_s3_bucket, aws_s3_bucket_cors_configuration

## Prompt

Create a S3 bucket with a CORS configuration that allows POSTs and GETs from my website "https://domain.com".

## Difficulty

2

## Intent

Has an aws_s3_bucket

Has an aws_s3_bucket_cors_configuration
with bucket = bucket id OR name
with cors rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["https://domain.com"]
  }

