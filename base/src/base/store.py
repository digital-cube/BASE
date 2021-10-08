class DictStore:
    store = {}

    def set(self, key, value):
        key = str(key)
        value = str(value).encode()
        DictStore.store[key] = value

    def get(self, key):
        key = str(key)
        return DictStore.store[key] if key in DictStore.store else None

    def flushall(self):
        DictStore.store = {}

    def rpush(self, queue_name, value):
        # print("RPUSH ",queue_name)
        pass

    def lpush(self, queue_name, value):
        # print("RPUSH ",queue_name)
        pass

    def rpop(self, queue_name):
        # print("RPOP",queue_name)
        return None

    def lpop(self, queue_name):
        # print("LPOP",queue_name)
        return None

    def brpop(self, queue_name, *args, **kwargs):
        # print("BRPOP",queue_name)
        return None

    def blpop(self, queue_name, *args, **kwargs):
        # print("BLPOP",queue_name)
        return None

    def exists(self, *names):
        ret = 0
        for key in names:
            if key in DictStore.store:
                ret += 1

        return ret

    def delete(self, *names):
        for key in names:
            if key in DictStore.store:
                del DictStore.store[key]


class Store:
    engine = DictStore()

    @staticmethod
    def set_engine(engine):
        if 'type' not in engine:
            raise NameError(f'Invalid engine, missing type')

        if engine['type'] not in ('redis', 'memory'):
            raise NameError(f"Store engine {engine} not supported")

        if engine['type'] == 'redis':
            import redis
            Store.engine = redis.Redis(host=engine['host'] if 'host' in engine else 'localhost',
                                       port=engine['port'] if 'port' in engine else '6379')

    @staticmethod
    def set(key, value):
        Store.engine.set(key, value)

    @staticmethod
    def get(key):
        return Store.engine.get(str(key))

    @staticmethod
    def rpush(queue_name, value):
        return Store.engine.rpush(str(queue_name), value)

    @staticmethod
    def lpush(queue_name, value):
        return Store.engine.rpush(str(queue_name), value)

    @staticmethod
    def lpop(key):
        return Store.engine.lpop(str(key))

    @staticmethod
    def rpop(key):
        return Store.engine.rpop(str(key))

    @staticmethod
    def blpop(key, *args, **kwargs):
        return Store.engine.blpop(str(key), *args, **kwargs)

    @staticmethod
    def brpop(key, *args, **kwargs):
        return Store.engine.brpop(str(key), *args, **kwargs)

    @staticmethod
    def exists(*names):
        return Store.engine.exists(*names)

    @staticmethod
    def flushall():
        Store.engine.flushall()

    @staticmethod
    def delete(*names):
        Store.engine.delete(*names)


def set(key, value):
    Store.set(key, value)


def get(key):
    return Store.get(str(key))


def exists(*names):
    return Store.exists(*names)


def flushall():
    Store.flushall()


def rpush(queue_name, value):
    Store.rpush(queue_name, value)


def lpush(queue_name, value):
    Store.lpush(queue_name, value)


def delete(*names):
    "Delete one or more keys specified by ``names``"
    Store.delete(*names)


def lpop(key):
    return Store.engine.lpop(str(key))


def rpop(key):
    return Store.engine.rpop(str(key))


def blpop(key, *args, **kwargs):
    return Store.engine.blpop(str(key), *args, **kwargs)


def brpop(key, *args, **kwargs):
    return Store.engine.brpop(str(key), *args, **kwargs)
