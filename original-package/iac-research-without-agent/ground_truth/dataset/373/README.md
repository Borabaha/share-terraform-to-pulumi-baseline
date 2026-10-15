# Prompt 373

## Resources

aws_lightsail_disk, aws_lightsail_disk_attachment, aws_lightsail_instance, aws_availability_zones

## Prompt

Set up a storage unit in Lightsail and link it with a Lightsail compute service.

## Difficulty

3

## Intent

have one aws_lightsail_disk resource
    with name
    with size_in_gb
    with availability_zone

have one aws_lightsail_disk_attachment
    with disk_name
    with instance_name
    with disk_path

have one "aws_lightsail_instance" resource
    with "name" argument
    with "availability_zone" argument
    with "blueprint_id" argument
    with "bundle_id" argument

