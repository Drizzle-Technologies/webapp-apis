import os
import redis

red = redis.StrictRedis(os.environ["REDIS_URI"])

