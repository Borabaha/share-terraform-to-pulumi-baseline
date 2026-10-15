package netflix_middle

import data.set
import rego.v1

default valid := false
default bucket_valid := false
default access_control_valid := false
default distribution_valid := false
default zone_valid := false
default record_valid := false

# S3 Bucket validation
bucket_valid if {
    some bucket in input.configuration.root_module.resources
    bucket.type == "aws_s3_bucket"
}

# CloudFront Origin Access Control validation
access_control_valid if {
    some access_control in input.configuration.root_module.resources
    access_control.type == "aws_cloudfront_origin_access_control"

    access_control.expressions.name
    access_control.expressions.origin_access_control_origin_type.constant_value == "s3"
    access_control.expressions.signing_behavior
    access_control.expressions.signing_protocol
}

# CloudFront Distribution validation
distribution_valid if {
    some distribution in input.configuration.root_module.resources
    distribution.type == "aws_cloudfront_distribution"

    some access_control in input.configuration.root_module.resources
    access_control.type == "aws_cloudfront_origin_access_control"

    some bucket in input.configuration.root_module.resources
    bucket.type == "aws_s3_bucket"

    some origin in distribution.expressions.origin
    bucket.address in origin.domain_name.references
    access_control.address in origin.origin_access_control_id.references

    some cache_behavior in distribution.expressions.default_cache_behavior
    {method | method := cache_behavior.allowed_methods.constant_value[_]} == {"GET", "HEAD"}
    {method | method := cache_behavior.cached_methods.constant_value[_]} == {"GET", "HEAD"}
    cache_behavior.viewer_protocol_policy.constant_value == "allow-all"

    origin.origin_id == cache_behavior.target_origin_id

    some restrictions in distribution.expressions.restrictions
    some restriction in restrictions.geo_restriction
    restriction.restriction_type
    restriction.locations
}

# Route 53 Zone validation
zone_valid if {
    some zone in input.configuration.root_module.resources
    zone.type == "aws_route53_zone"

    zone.expressions.name
}

# Route 53 Record validation
record_valid if {
    some record in input.configuration.root_module.resources
    record.type == "aws_route53_record"

    some zone in input.configuration.root_module.resources
    zone.type == "aws_route53_zone"

    some distribution in input.configuration.root_module.resources
    distribution.type == "aws_cloudfront_distribution"

    record.expressions.type
    record.expressions.name
    zone.address in record.expressions.zone_id.references

    some alias in record.expressions.alias
    distribution.address in alias.name.references
    distribution.address in alias.zone_id.references
    alias.evaluate_target_health
}

# Final validation check
valid if {
    bucket_valid
    access_control_valid
    distribution_valid
    zone_valid
    record_valid
}
