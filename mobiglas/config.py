import os
import sys
import json

import envparse

from .utils import find_in_dict

env = envparse.Env()
ROOT_DIR = os.path.abspath(os.path.join(__file__, os.path.pardir))


class _Settings(dict):
    """ Dictionary that allows you to access it's keys as attributes """

    def __getattr__(self, item):
        if item in self and isinstance(self[item], dict):
            self[item] = _Settings(self[item])
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value


settings = _Settings({
    "bot": {
        "name": env.str("BOT_NAME", default="mG.bot"),
        "token": env.str("BOT_TOKEN", default=""),
        "playing": env.str("BOT_PLAYING", default="with Humans"),
        "owners": env.list("BOT_OWNER_IDS", default=[]),
        "join_message": env.str("BOT_JOIN_MESSAGE", default="I has joined to do stuff 🌟"),
        "prefix": env.list("BOT_CMD_PREFIXES", default=["!"]),
        "admin_channels": env.list("BOT_ADMIN_CHANNEL_IDS", default=[]),
        "reserved": {
            "roles": env.list("BOT_RES_ROLES", default=["@everyone"]),
        },
        "gallery": {
            "enabled": env.bool("BOT_GALLERY_ENABLED", default=False),
            "name": env.bool("BOT_GALLERY_NAME", default="gallery")
        }
    },
    "org": {
        "sid": env.str("ORG_SID", default=""),
        "name": env.str("ORG_NAME", default=""),
        "url": env.str("ORG_URL", default="")
    },
    "sentry_dsn": {
        "enabled": env.bool("SENTRY_ENABLED", default=False),
        "url": env.url("SENTRY_DSN", default="")
    },
    "scorgsite": {
        "url": env.url("SCORGSITE_URL", default=""),
        "secret": env.str("SCORGSITE_SECRET", default=""),
    },
    "db": {
        "path": env.str("DB_PATH", default="/opt/mobiglas/db/mobiglas.db")
    },
    "logs": {
        "path": env.str("LOG_PATH", default="/opt/mobiglas/logs/mobiglas.log")
    },
    "data": {
        "welcome": {
            "enabled": env.bool("WELCOME_ENABLED", default=True),
            "channel": env.str("WELCOME_CHANNEL", default=0),
            "msg": env.str("WELCOME_MSG", default="")
        },
        "motion": {}
    }
})

# update default settings from config file if it exists
try:
    config_file = env.str("CONFIG_FILE", default=os.path.join(ROOT_DIR, "../config.json"))
    print(f"Loading config file: {config_file}")
    if os.path.isfile(config_file):
        with open(config_file, encoding='utf8') as config:
            settings.update(json.load(config))
except AttributeError:
    raise AttributeError("Unknown argument")

# todo: remove because everything is required
# Check for required configurations
REQUIRED_SETTINGS = [
    'bot.token',
    'org.sid',
    'org.name',
    'org.url',
    'scorgsite.url',
    'scorgsite.secret'
]

for key in REQUIRED_SETTINGS:
    v = ""
    try:
        v = find_in_dict(key, settings)
    except KeyError:
        pass
    finally:
        if not v:
            sys.stderr.write(f'Missing required settings: {key}')
