terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# DynamoDB Table with Correct Attribute Configuration
resource "aws_dynamodb_table" "example" {
  name         = "example"
  hash_key     = "TEST_KEY"  # Corrected to match the attribute name
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "TEST_KEY"
    type = "S"
  }
}

# Global Table Replication (Fix for Multi-Region Replicas)
resource "aws_dynamodb_global_table" "example" {
  provider = aws
  name     = aws_dynamodb_table.example.name

  replica {
    region_name = "us-east-1"
  }

  replica {
    region_name = "us-east-2"
  }

  replica {
    region_name = "us-west-2"
  }
}
