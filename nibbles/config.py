import sqlite3
from dataclasses import dataclass
from pathlib import Path

import tomli
from dotenv import dotenv_values

project_path = Path(__file__).parent
with open(project_path.joinpath('config').joinpath('config.toml'), 'rb') as f:
    settings = tomli.load(f)

_env = dotenv_values(project_path.joinpath("config").joinpath("tokens"))
discord_token = _env[settings['TOKEN']]
del _env

to_sync = settings['SYNC']


# guild for testing
@dataclass
class guild:
    id: int


if (settings['TOKEN'] == 'TEST_TOKEN'):
    guilds = (guild(805821298193465384),)
else:
    guilds = []

# databases
user_db = sqlite3.connect(project_path.joinpath("db").joinpath("user.db"))
todo_json = project_path.joinpath("db").joinpath("todo.json")
servers_db = sqlite3.connect(project_path.joinpath("db").joinpath("servers.db"))
""" genshin info """
# banner_info_txt = project_path.joinpath("db").joinpath("banner_info.txt")
# char_db = sqlite3.connect(project_path.joinpath("db").joinpath("char.db"))
# ginv_json = project_path.joinpath("db").joinpath("genshin_inventory.json")
# pity_db = sqlite3.connect(project_path.joinpath("db").joinpath("pity.db"))

"""job scheduling"""
jobs_db = f'sqlite:///{Path("nibbles").joinpath("db").joinpath("jobs.db")}'
config_timezone = 'US/Central'
log_level = 'INFO'

"""image generation"""
media_dir = project_path.joinpath("media")
