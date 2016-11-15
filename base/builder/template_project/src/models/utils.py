from sqlalchemy import Column, String, Integer
import common.orm


class Options(common.orm.sql_base):

    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    key = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)

    def __init__(self, key, value):

        self.key = key
        self.value = value


def main():

    _session = common.orm.orm.session()

    import src.config.app_config
    _o = Options('version', src.config.app_config.app_version)
    _session.add(_o)
    _session.commit()


if __name__ == '__main__':

    main()
