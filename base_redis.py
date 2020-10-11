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

 #    def __init__(self, *args, **kwargs):
 #        if 'password' not in kwargs:
 #            self.redis_password = os.getenv('REDIS_PASSWORD')
 # #           if not self.redis_password:
 # #               raise NameError("REDIS_PASSWORD environment variable is required")
 #
 #            if self.redis_password:
 #                kwargs['password'] = self.redis_password
 #        else:
 #            self.redis_password = kwargs['password']
 #
 #        if 'port' not in kwargs:
 #            self.redis_port = os.getenv('REDIS_PORT')
 #            if self.redis_port:
 #                kwargs['port']=self.redis_port
 #
 #        if 'host' not in kwargs:
 #            self.redis_host = os.getenv('REDIS_HOST')
 #            if self.redis_host:
 #                kwargs['host']=self.redis_host
 #
 #        super().__init__(*args, **kwargs)
 #
 #    def __del__(self):
 #        if self.redis_password:
 #            super().__del__()
 #
 #    pass
