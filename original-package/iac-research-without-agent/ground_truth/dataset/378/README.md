# Prompt 378

## Resources

aws_lightsail_distribution, aws_lightsail_instance, aws_lightsail_static_ip, aws_lightsail_static_ip_attachment, aws_availability_zones

## Prompt

managing an AWS Lightsail Distribution with a instance as an origin

## Difficulty

3

## Intent

have one aws_lightsail_instance
    with "name" argument
    with "availability_zone" argument
    with "blueprint_id" argument
    with "bundle_id" argument

have one aws_lightsail_distribution
    with name
    with bundle_id
    with default_cache_behavior 
        with behavior
    with origin 
        with name
        with region_name
    with cache_behavior_settings 
        with forwarded_cookies
            with cookies_allow_list 
        with forwarded_headers  
            with headers_allow_list 
        with forwarded_query_strings 
            with query_strings_allowed_list


