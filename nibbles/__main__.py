import asyncio
from datetime import datetime, date, timedelta
import time
import threading

import discord
from discord.ext import commands, tasks

from nibbles.config import guilds, discord_token, to_sync

"""
Define Bot Attributes
"""

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='',
                         intents=discord.Intents(guilds=True, members=True, messages=True),
                         case_insensitive=True)

    async def on_ready(self):
        await self.load_extension('nibbles.cogs.misc')
        await self.load_extension('nibbles.cogs.econ')
        await self.load_extension('nibbles.cogs.todo')
        await self.load_extension('nibbles.cogs.remind')
        await self.wait_until_ready()

        # set in config whether to sync
        if to_sync:
            print(await self.tree.sync())
            for _id in guilds:
                print(await self.tree.sync(guild=_id))
        print("bot online")

        client.launch_midnight = threading.Thread(target=launch_tasks)
        if not client.launch_midnight.is_alive():
            client.launch_midnight.start()


client = Bot()
# econ.init_db()


def launch_tasks():
    asyncio.set_event_loop(client.loop)
    now = datetime.now()
    midnight = datetime.combine(date.today() + timedelta(days=1), datetime.min.time()) + timedelta(hours=9)
    tdelta = midnight - now
    midnight_time = tdelta.total_seconds() % (24 * 3600)
    print(f'{midnight_time / 3600} hours until tasks launch')
    threading.Timer(midnight_time, daily_reset).start()

def daily_reset():
    econ = client.get_cog('Econ')
    if econ is not None:
        econ.spun_today = {}
    threading.Timer(60*60*24, daily_reset).start()


@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    if ctx.valid:
        await client.process_commands(message)

client.run(discord_token)