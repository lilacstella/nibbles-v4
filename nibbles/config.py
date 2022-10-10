from dataclasses import dataclass
import sqlite3
from pathlib import Path

from dotenv import dotenv_values

to_sync = False


# guild for testing
@dataclass
class guild:
    id: int


# guilds = (guild(805821298193465384), guild(607298393370394625), guild(805821298193465384))
# guilds = (guild(805821298193465384), )
guilds = []

project_path = Path(__file__).parent

# databases
user_db = sqlite3.connect(project_path.joinpath("db").joinpath("user.db"))
todo_json = project_path.joinpath("db").joinpath("todo.json")
""" genshin info """
# banner_info_txt = project_path.joinpath("db").joinpath("banner_info.txt")
# char_db = sqlite3.connect(project_path.joinpath("db").joinpath("char.db"))
# ginv_json = project_path.joinpath("db").joinpath("genshin_inventory.json")
# pity_db = sqlite3.connect(project_path.joinpath("db").joinpath("pity.db"))

"""job scheduling"""
jobs_db = f'sqlite:///{Path("nibbles").joinpath("db").joinpath("jobs.sqlite")}'
config_timezone = 'US/Central'
log_level = 'INFO'

# values
_env = dotenv_values(project_path.joinpath("secrets").joinpath("tokens"))
discord_token = _env["DISCORD_TOKEN"]
dbl_token = _env["DBL_TOKEN"]
del _env
