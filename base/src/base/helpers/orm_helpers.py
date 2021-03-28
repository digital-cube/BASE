import uuid
import datetime

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

                if _type in (datetime.datetime, uuid.UUID, ):
                    res[field] = str(getattr(self, field))
                else:
                    res[field] = getattr(self, field)

        return res
