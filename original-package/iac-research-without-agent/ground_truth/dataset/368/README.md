# Prompt 368

## Resources

aws_lightsail_database

## Prompt

create AWS Lightsail that creates a mysql database. It should allow daily backups to take place between 16:00 and 16:30 each day and  requires any maintiance tasks (anything that would cause an outage, including changing some attributes) to take place on Tuesdays between 17:00 and 17:30

## Difficulty

2

## Intent

have one "aws_lightsail_database" resource
    with relational_database_name argument
    with master_database_name 
    with master_password
    with master_username
    with blueprint_id
    with bundle_id
    with  preferred_backup_window    = "16:00-16:30"
  preferred_maintenance_window = "Tue:17:00-Tue:17:30"

    

