import uuid
import datetime
import asyncpg.pgproto.pgproto
import tortoise.timezone


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
                attr_value = getattr(self, field)
                _type = type(attr_value)

                if attr_value is None:
                    res[field] = None
                elif _type in (uuid.UUID, asyncpg.pgproto.pgproto.UUID):
                    res[field] = str(attr_value)
                elif _type in (datetime.datetime,):
                    if tortoise.timezone.is_aware(attr_value):
                        res[field] = str(tortoise.timezone.make_naive(attr_value))

                else:
                    res[field] = attr_value


        return res

    def match(self, data: dict):
        for field in data:
            if not hasattr(self, field):
                return False
            if getattr(self, field) != data[field]:
                return False

        return True


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
