output "cloudtrail_name" {
  value = aws_cloudtrail.main_trail.name
  # Output any necessary information
}

output "s3_bucket_name" {
  value = aws_s3_bucket.cloudtrail_logs.bucket
}