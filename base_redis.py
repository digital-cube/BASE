import redis
import os


class Redis(redis.Redis):
    def __init__(self, *args, **kwargs):
        if 'password' not in kwargs:
            self.redis_password = os.getenv('REDIS_PASSWORD')
            if not self.redis_password:
                raise NameError("REDIS_PASSWORD environment variable is required")

            kwargs['password'] = self.redis_password

        super().__init__(*args, **kwargs)

    def __del__(self):
        if self.redis_password:
            super().__del__()

    pass
