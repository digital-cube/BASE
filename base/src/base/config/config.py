import os
import sys
import logging
import logging.config

import asyncio
import aiotask_context as context


class config:
    """Config pre-filled with default Options"""
    conf: dict = {}

    initialized = False

    @staticmethod
    def load_from_dict(config_dictionary: dict) -> None:
        """
        Load App configuration from a dictionary

        :param config_dictionary: The dictionary with the settings for the App.
        """
        
        # if config.initialized:
        #     return
        
        
        config.load_default_options()

        config.conf.update(config_dictionary)

        from ..registry import register
        register(config_dictionary)
        # config.initialized = True

    @staticmethod
    def __parse_yaml(path: str) -> dict:
        """
        Helper function for parsing a YAML file and returning a dictionary created from the parsed YAML file

        :param path: Path to the YAML file
        :return: Dictionary createad from the YAML file
        """
        import yaml

        # Load App config from config.yaml
        try:
            with open(path) as file:
                config_yaml = yaml.load(file, Loader=yaml.SafeLoader)
        except Exception as e:
            print(e)
            sys.exit()

        def use_value_from_env(d):
            '''
            TODO:
            :param d:
            :return:
            '''
            for key in d:
                v = d[key]
                if type(v) == dict:
                    use_value_from_env(v)
                elif type(v) == str and len(v) > 0 and v[0] == '$':
                    d[key] = os.getenv(v[1:], '')

        use_value_from_env(config_yaml)

        return config_yaml

    @staticmethod
    def load_from_yaml(path: str) -> None:
        """
        Function which loads the Application from the
        :param path:
        """

        # if config.initialized:
        #     return
        
        config.load_default_options()

        config.conf.update(config.__parse_yaml(path))

        if 'keys' in config.conf:
            try:
                with open(config.conf['keys']['private']) as pkey:
                    config.conf['keys']['private'] = pkey.read()
                with open(config.conf['keys']['public']) as pubkey:
                    config.conf['keys']['public'] = pubkey.read()
            except Exception as e:
                print(e)
                sys.exit()

        from ..registry import register
        register(config.conf)
        # config.initialized = True

    @staticmethod
    def load_default_options():
        import os
        config.conf = config.__parse_yaml(os.path.dirname(os.path.realpath(__file__)) + '/config.example.yaml')

    @staticmethod
    def load_private_key(path: str) -> None:
        with open(path) as pkey:
            config.conf.update({'private_key': pkey.read()})

    @staticmethod
    def init_logging():
        from ..app import Base

        logging.config.dictConfig(config.conf['logging'])
        Base.logger = logging.getLogger(config.conf.get('logging')['request_logger'])
        loop = asyncio.get_event_loop()
        loop.set_task_factory(context.task_factory)

    @staticmethod
    def tortoise_config() -> dict:
        """
        Get parts of the configuration used for initialising Tortoise ORM and
        make sure the structure of the config is adjusted
        :return: dict
        """
        tort_conf = config.conf['tortoise']

        # for connection in tort_conf['connections']:
        #     tort_conf['connections'][connection]['credentials'] = {
        #         'host': config.conf['db']['host'],
        #         'port': config.conf['db']['port'],
        #         'user': config.conf['db']['username'],
        #         'password': config.conf['db']['password'],
        #         'database': config.conf['db']['database'],
        #     }

        return tort_conf


config.load_default_options()
