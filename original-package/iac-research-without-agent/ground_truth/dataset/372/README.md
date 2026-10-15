# Prompt 372

## Resources

aws_lightsail_disk, aws_lightsail_disk_attachment, aws_lightsail_instance, aws_availability_zones

## Prompt

Create a Lightsail Disk resource and attaches the Lightsail disk to a Lightsail Instance

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

