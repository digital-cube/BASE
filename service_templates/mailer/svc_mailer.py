from base import Base
import base.registry

base.registry.register("users", {"port": 9102,
                                 "prefix": "/api/mailer",
                                 'sendgrid_api_key': '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',
                                 "db":
                                     {
                                         "type": "postgresql",
                                         "port": "5432",
                                         "host": "localhost",
                                         "username": "sfscon",
                                         "password": "123",
                                         "database": "sfscon_mailer"
                                     }
                                 }
                       )

import orm.orm
import api.mailer

if __name__ == "__main__":
    print(f"starting users service on :{base.registry.port()}")
    base.Base.run(port=base.registry.port())
