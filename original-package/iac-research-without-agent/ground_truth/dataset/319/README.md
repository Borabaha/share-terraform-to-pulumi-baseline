# Prompt 319

## Resources

aws_cloudfront_distribution, aws_cloudfront_origin_access_control, aws_route53_record, aws_route53_record, aws_route53_zone, aws_s3_bucket

## Prompt

An AWS CloudFront distribution resource with an origin argument block with the following arguments (1) a domain_name argument linking to the S3 backet domain name; (2) an origin_access_control_id argument linking to a CloudFront origin access control resource; (3) an origin_id argument with value "s3_video_content_origin", a default_cache_behavior argument with the following arguments (a) an allowed_methods argument with values ["GET", "HEAD"]; (b) a cached_methods with values ["GET", "HEAD"]; (c) a target_origin_id argument with value "s3_video_content_origin" (same as origin_id in the origin argument block); (d) a viewer_protocol_policy argument with value "allow-all"; (4) a price_class argument with value "PriceClass_200"; (5) a restrictions argument block with a geo_restriction argument block with a restriction_type argument of value "whitelist" and locations argument with values ["US", "CA", "GB", "DE"]; (6) a viewer_certificate argument block with cloudfront_default_certificate set to true. An AWS Route53 zone resource with a name argument of value "netflix.com". Two AWS Route53 record resources linking to the Route53 hosted zone. A CloudFront origin access control resource with (1) a name argument; (2) an origin_access_control_origin_type argument of value "s3"; (3) a signing_behavior argument of value "always"; (4) a signing_protocol argument of value "sigv4".

## Difficulty

6

## Intent

have one "aws_cloudfront_origin_access_control" resource
    with "name" argument
    with "origin_access_control_origin_type" with value "s3"
    with "signing_behavior" argument with value "always"
    with "signing_protocol" argument with value "sigv4"

have one "aws_cloudfront_distribution" resource
    with "origin.domain_name" argument linking to "aws_s3_bucket" resource
    with "origin.origin_access_control_id" argument linking to "aws_cloudfront_origin_access_control" resource
    with "origin.origin_id" argument with value x
    with "default_cache_behavior.allowed_methods" argument with value ["GET", "HEAD"]
    with "default_cache_behavior.cached_methods" argument with value ["GET", "HEAD"]
    with "default_cache_behavior.target_origin_id" argument with value x
    with "default_cache_behavior.viewer_protocol_policy" argument with value "allow-all"
    with "price_class" argument with value "PriceClass_200"
    with "restrictions.geo_restriction.restriction_type" argument with value "whitelist"
    with "restrictions.geo_restriction.locations" argument with value ["US", "CA", "GB", "DE"]
    with "viewer_certificate.cloudfront_default_certificate" argument with value true

have one "aws_s3_bucket" resource

have one "aws_route53_zone" resource
    with "name" argument with value "netflix.com"

have one "aws_route53_record" resource
    with "type" argument with value "A"
    with "name" argument with value "cdn"
    with "zone_id" argument linking to "aws_route53_zone" resource

    with "alias.name" argument linking to "aws_cloudfront_distribution" resource
    with "alias.zone_id" argument linking to "aws_cloudfront_distribution" resource
    with "alias.evaluate_target_health" argument with value true

have one "aws_route53_record" resource
    with "type" argument with value "AAAA"
    with "name" argument with value "cdn"
    with "zone_id" argument linking to "aws_route53_zone" resource

    with "alias.name" argument linking to "aws_cloudfront_distribution" resource
    with "alias.zone_id" argument linking to "aws_cloudfront_distribution" resource
    with "alias.evaluate_target_health" argument with value true

