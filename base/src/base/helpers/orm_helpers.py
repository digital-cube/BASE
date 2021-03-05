class BaseOrmHelpers:

    def serialize(self, fields: tuple = ()):
        return self._serialize(forbidden_fields=set(), ordered_default_fields=fields)

    def _serialize(self, forbidden_fields: set = set(), ordered_default_fields: tuple = ()):

        if not ordered_default_fields:
            ordered_default_fields = [k for k in self.__dict__.keys()
                                      if not k.startswith('_') and not k.endswith('_') and k not in forbidden_fields]
        else:
            ordered_default_fields = [k for k in ordered_default_fields if k not in forbidden_fields]

        res = {}
        for field in ordered_default_fields:
            if hasattr(self, field):
                res[field] = getattr(self, field)

        return res