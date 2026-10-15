resource "aws_s3_bucket" "mybucket" {
  bucket = "mybucket"
}

resource "aws_s3_bucket_metric" "example-entire-bucket" {
  bucket = aws_s3_bucket.mybucket.id
  name   = "EntireBucket"
}