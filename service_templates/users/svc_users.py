from base import Base
import base.registry
import os

base.registry.register("users", {
    'port': os.getenv('APP_PORT', 9203),
    "prefix": "/api/users",
    "db":
        {
            "type": "postgresql",
            "port": "5432",
            "host": "localhost",
            "username": "telmekom",
            "password": "123",
            "database": "tc_users"
        }
})

import orm.orm
import api.clients

if __name__ == "__main__":
    print(f"starting users service on :{base.registry.port()}")
    base.Base.run(port=base.registry.port())
