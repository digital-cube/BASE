from base import Base
import base.registry

base.registry.register("users", {"port": 9100,
                                 "prefix": "/api/users",
                                 "db":
                                     {
                                         "type": "postgresql",
                                         "port": "5432",
                                         "host": "localhost",
                                         "username": "telmekom",
                                         "password": "123",
                                         "database": "telmekom_web_users"
                                     }
                                 })

import orm.orm
import api.users

if __name__ == "__main__":
    print(f"starting users service on :{base.registry.port()}")
    base.Base.run(port=base.registry.port())
