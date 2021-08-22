import os
import json
from logging import config, getLogger
from . import util

LOG_PATH = "../log"


def get_logger(context):
    name = util.get_addon_name()
    level = "DEBUG" if util.get_pref(context).is_debug else "WARN"
    logging_settings(name, level)
    return getLogger(name)


def logging_settings(name, level):
    console_formatter_name = name + ".formatter"
    console_handler_name = name + ".console"
    debug_handler_name = name + ".debug"
    error_formatter_name = name + ".errorformatter"
    error_handler_name = name + ".error"
    base_log_dir = os.path.join(os.path.dirname(__file__), LOG_PATH)
    configure = {
        "version": 1,
        "formatters": {
            console_formatter_name: {
                "format": json.dumps({
                    "time": r"%(asctime)s",
                    "level": r"%(levelname)s",
                    "name": r"%(name)s",
                    "message": r"%(message)s",
                })
            },
            error_formatter_name: {
                "format": json.dumps({
                    "time": r"%(asctime)s",
                    "level": r"%(levelname)s",
                    "name": r"%(name)s",
                    "message": r"%(message)s",
                })
            }
        },
        "handlers": {
            console_handler_name: {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": console_formatter_name,
            },
            debug_handler_name: {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "filename": os.path.join(base_log_dir, "debug.log"),
                "maxBytes": 1024 * 1024,
                "backupCount": 5,
                "formatter": console_formatter_name,
            },
            error_handler_name: {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "filename": os.path.join(base_log_dir, "error.log"),
                "maxBytes": 1024 * 1024,
                "backupCount": 5,
                "formatter": error_formatter_name,
            },
        },
        "loggers": {
            name: {
                "level": level,
                "handlers": [
                    console_handler_name,
                    debug_handler_name,
                    error_handler_name,
                ],
                "propagate": False
            }
        },
        "disable_existing_loggers": False
    }
    config.dictConfig(configure)
