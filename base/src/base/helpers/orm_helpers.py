import uuid
import datetime
import asyncpg.pgproto.pgproto

class BaseOrmHelpers:

    def serialize(self, fields: tuple = ()):
        return self._serialize(ordered_default_fields=fields)

    def _serialize(self, forbidden_fields: tuple = (), ordered_default_fields: tuple = ()):

        if not ordered_default_fields:
            ordered_default_fields = [k for k in self.__dict__.keys()
                                      if not k.startswith('_') and not k.endswith('_') and k not in forbidden_fields]
        else:
            ordered_default_fields = [k for k in ordered_default_fields if k not in forbidden_fields]

        res = {}
        for field in ordered_default_fields:
            if hasattr(self, field):
                _type = type(getattr(self, field))

                if _type in (datetime.datetime, uuid.UUID, asyncpg.pgproto.pgproto.UUID):
                    res[field] = str(getattr(self, field))
                else:
                    res[field] = getattr(self, field)

        return res

    def update(self, data: dict):
        return self._update(forbidden_fields=('id',), data=data)
        pass

    def _update(self, forbidden_fields=('id',), data: dict = {}):

        updated = []
        for field in data:
            if field in forbidden_fields:
                continue

            if hasattr(self, field):
                if getattr(self, field) != data[field]:
                    setattr(self, field, data[field])
                    updated.append(field)

        return updated
