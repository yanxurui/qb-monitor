import json
import os
import logging

get_time = lambda f: os.stat(f).st_ctime

class Config:
    _config = None
    _config_file_name = 'config.json'
    _config_file_prev_modified_time = None

    @classmethod
    def get_config(cls, update=False):
        if not cls._config or update and cls.is_config_file_updated():
            logging.info('reload config')
            cls._config = None
            with open(cls._config_file_name, 'r') as f:
                # Reading from json file
                cls._config = json.load(f)
        return cls._config

    @classmethod
    def is_config_file_updated(cls):
        t = get_time(cls._config_file_name)
        if t != cls._config_file_prev_modified_time:
            cls._config_file_prev_modified_time = t
            return True
        return False
