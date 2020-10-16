import redis
import os


class Redis(redis.Redis):
    def __init__(self, *args, **kwargs):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = os.getenv('REDIS_PORT', '6379')

#        print("BASE::REDIS_INIT_ON(",redis_host, redis_port,")")

        if 'host' not in kwargs:
            kwargs['host'] = redis_host

        if 'port' not in kwargs:
            kwargs['port'] = redis_port

        super().__init__(*args, **kwargs)

    def __del__(self):
        super().__del__()
