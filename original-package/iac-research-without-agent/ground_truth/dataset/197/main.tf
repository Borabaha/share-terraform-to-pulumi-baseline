resource "aws_elasticache_user" "test" {
  user_id       = "testUserId"
  user_name     = "default"
  access_string = "on ~app::* -@all +@read +@hash +@bitmap +@geo -setbit -bitfield -hset -hsetnx -hmset -hincrby -hincrbyfloat -hdel -bitop -geoadd -georadius -georadiusbymember"
  engine        = "REDIS"
  passwords     = ["password123456789"]
}

resource "aws_elasticache_user" "test1" {
  user_id       = "testUserId1"
  user_name     = "default1"
  access_string = "on ~app::* -@all +@read +@hash +@bitmap +@geo -setbit -bitfield -hset -hsetnx -hmset -hincrby -hincrbyfloat -hdel -bitop -geoadd -georadius -georadiusbymember"
  engine        = "REDIS"
  passwords     = ["password1234567891"]
}

resource "aws_elasticache_user" "test2" {
  user_id       = "testUserId2"
  user_name     = "default2"
  access_string = "on ~app::* -@all +@read +@hash +@bitmap +@geo -setbit -bitfield -hset -hsetnx -hmset -hincrby -hincrbyfloat -hdel -bitop -geoadd -georadius -georadiusbymember"
  engine        = "REDIS"
  passwords     = ["password1234567892"]
}

resource "aws_elasticache_user_group" "test" {
  engine        = "REDIS"
  user_group_id = "userGroupId"
  user_ids      = [aws_elasticache_user.test.user_id, aws_elasticache_user.test1.user_id, aws_elasticache_user.test2.user_id]
}