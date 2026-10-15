terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.75"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    ec2        = "http://localhost:4566"
    iam        = "http://localhost:4566"
    s3         = "http://localhost:4566"
    sts        = "http://localhost:4566"
  }
}

# ---- VPC Setup (Works in LocalStack) ----
resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
}

# Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

# Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
}

# Internet Gateway (Not needed for LocalStack but included for completeness)
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.my_vpc.id
}

# ---- Hardcoded AMI (For LocalStack Only) ----
variable "default_ami" {
  default = "ami-12345678"  # Fake AMI for LocalStack
}

# ---- Launch Template ----
resource "aws_launch_template" "ec2_launch_template" {
  name          = "my-launch-template"
  instance_type = "t2.micro"
  image_id      = var.default_ami  # Use hardcoded AMI

  network_interfaces {
    associate_public_ip_address = true
    subnet_id                   = aws_subnet.public_subnet.id
  }
}

# ---- Auto Scaling Group (Works in LocalStack) ----
resource "aws_autoscaling_group" "asg" {
  desired_capacity    = 2
  max_size           = 5
  min_size           = 1
  vpc_zone_identifier = [aws_subnet.public_subnet.id]

  launch_template {
    id      = aws_launch_template.ec2_launch_template.id
    version = "$Latest"
  }
}

# ---- IAM Role for EC2 ----
resource "aws_iam_role" "role" {
  name = "my-ec2-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      }
    }
  ]
}
EOF
}

# ---- IAM Policy ----
resource "aws_iam_role_policy" "policy" {
  name = "my-ec2-policy"
  role = aws_iam_role.role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

