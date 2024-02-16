provider "aws" {
  region = var.aws_region
  # Credentials are automatically sourced from environment variables
}

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket        = var.bucket_name
  force_destroy = true
}

resource "aws_cloudtrail" "main_trail" {
  name                          = "main-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_policy" "cloudtrail_logs_policy" {
  bucket = var.bucket_name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {"Service": "cloudtrail.amazonaws.com"},
        Action = "s3:GetBucketAcl",
        Resource = "arn:aws:s3:::${var.bucket_name}"
      },
      {
        Effect = "Allow",
        Principal = {"Service": "cloudtrail.amazonaws.com"},
        Action = "s3:PutObject",
        Resource = "arn:aws:s3:::${var.bucket_name}/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
        Condition = {StringEquals = {"s3:x-amz-acl": "bucket-owner-full-control"}}
      }
    ]
  })
}