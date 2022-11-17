# nibbles-v4

## Config
in nibbles/config:

`DISCORD_TOKEN` and `DBL_TOKEN` in `tokens` file

in `config`, the `config.toml` file specifies:

 - `TOKEN` the name of the discord token in `tokens`
 - `SYNC` whether to sync the commands to discord


## Databases
 - user.db
 - todo.json
 - banner_info.txt
 - char.db
 - genshin_inventory.json
 - pity.db

## Installation and Execution
```python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m nibbles
```
