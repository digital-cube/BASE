import os
import sys
import copy
import logging
import logging.config

import asyncio
import aiotask_context as context
from typing import Union


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

        if config.initialized:
            return

        config.load_default_options()

        config.update_conf(config_dictionary)

        from ..registry import register
        register(config_dictionary)
        config.initialized = True

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

        if config_yaml is None:
            return {}

        def use_value_from_env(d):
            '''
            Read value for configuration from an environment variable with the same name as in the config file
            :param d: dict - dictionary of settings from yaml file or nested configuration
            :return: void
            '''
            if not d:
                d = {}
                return

            for key in d:
                v = d[key]
                if type(v) == dict:
                    use_value_from_env(v)
                elif type(v) == str and len(v) > 0 and v[0] == '$':
                    d[key] = os.getenv(v[1:], '')

        use_value_from_env(config_yaml)
        # trace if client defined it's own configuration
        config_yaml["default_config"] = True

        return config_yaml

    @staticmethod
    def update_conf(new_conf) -> None:
        # config.conf.update(new_conf)

        def _update_conf(old_conf, new_conf):
            for k in new_conf:
                if k not in old_conf:
                    old_conf[k] = new_conf[k]
                else:
                    value_type = type(new_conf[k])
                    if value_type != dict:
                        if value_type == list:
                            if old_conf[k]:
                                old_conf[k].extend(new_conf[k])
                            else:
                                old_conf[k] = new_conf[k]
                        else:
                            old_conf[k] = new_conf[k]
                    else:
                        _update_conf(old_conf[k], new_conf[k])

        _update_conf(config.conf, new_conf)

    @staticmethod
    def load_from_yaml(paths: Union[str, list]) -> None:
        """
        Function which loads the Application from the
        :param path:
        """

        if config.initialized:
            return

        config.load_default_options()

        if type(paths) == str:
            config.update_conf(config.__parse_yaml(paths))
        else:
            for path in paths:
                config.update_conf(config.__parse_yaml(path))

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
        config.initialized = True
        config.conf["default_config"] = False

    @staticmethod
    def load_default_options():
        import os
        config.conf = config.__parse_yaml(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml')

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
        tort_conf = copy.deepcopy(config.conf['tortoise'])

        # remove unwanted parts
        for connection in tort_conf['connections']:
            if 'type' in tort_conf['connections'][connection]['credentials']:
                del tort_conf['connections'][connection]['credentials']['type']

        return tort_conf

    @staticmethod
    def get_db_url(test=False) -> str:
        """
        Get database connection url, e.g.:
        postgres://_username_:123@127.0.0.1:5432/test_openwaste_users

        :return: str - db url
        """

        _db_name = f'{"test_" if test else ""}{config.conf["db"]["database"]}'
        return f'postgres://{config.conf["db"]["user"]}:{config.conf["db"]["password"]}@{config.conf["db"]["host"]}:{config.conf["db"]["port"]}/{_db_name}'



config.load_default_options()
