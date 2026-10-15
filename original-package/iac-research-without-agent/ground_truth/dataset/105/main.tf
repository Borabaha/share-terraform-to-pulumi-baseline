provider "aws" {
    region = "us-west-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket        = "metricbeat-test-bucket"
  force_destroy = true // Required for cleanup
}

resource "aws_s3_bucket_metric" "my_bucket_metric" {
  bucket = aws_s3_bucket.my_bucket.id
  name   = "EntireBucket"
}

resource "aws_s3_bucket_object" "my_bucket_object" {
  key     = "someobject"
  bucket  = aws_s3_bucket.my_bucket.id
  content = "something"
}