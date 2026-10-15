terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.75"
    }
  }

  }

provider "aws" {
  region = "us-east-1"
  profile = "admin-1"

  assume_role {
    role_arn = "arn:aws:iam::590184057477:role/yicun-iac"
  }
}

resource "aws_s3_bucket" "wellcomecollection-platform-infra" {
  bucket_prefix = "wellcomecollection-platform-infra-"
}

resource "aws_s3_bucket_ownership_controls" "example" {
    bucket = aws_s3_bucket.wellcomecollection-platform-infra.id
    rule {
        object_ownership = "BucketOwnerPreferred"
    }
}

resource "aws_s3_bucket_acl" "wellcomecollection-platform-infra" {
  depends_on = [ aws_s3_bucket_ownership_controls.example ]

  bucket = aws_s3_bucket.wellcomecollection-platform-infra.id
  acl    = "private"
}

resource "aws_s3_bucket_lifecycle_configuration" "wellcomecollection-platform-infra" {
  bucket = aws_s3_bucket.wellcomecollection-platform-infra.id

  rule {
    id = "tmp"

    filter {
      prefix = "tmp/"
    }

    expiration {
      days = 30
    }

    status = "Enabled"
  }

  rule {
    id = "expire_old_versions"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "wellcomecollection-platform-infra" {
  bucket = aws_s3_bucket.wellcomecollection-platform-infra.id

  versioning_configuration {
    status = "Enabled"
  }
}