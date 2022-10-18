import random
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from nibbles.config import guilds
from nibbles.config import user_db as conn
from nibbles.utils.pillow import generate_lb


class XP(commands.GroupCog, name="xp"):

    def __init__(self, client):
        self.client = client
        self.voice = {}
        self.text = {}
        c = conn.cursor()
        for guild in self.client.guilds:
            c.execute(f"CREATE TABLE IF NOT EXISTS s{guild.id} (user_id INTEGER PRIMARY KEY, xp INTEGER)")
        conn.commit()

    # when join server, make table for xp
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        c = conn.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS s{guild.id} (user_id INTEGER PRIMARY KEY, xp INTEGER)")
        conn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return
        user_id = message.author.id
        val = random.randrange(25, 43)
        c = conn.cursor()
        # if bal does not exist, add user
        c.execute(f"INSERT OR IGNORE INTO users VALUES (?, 0, 160, '', '')", (user_id,))
        # if xp does not exist, add xp table and user
        c.execute(f"INSERT OR IGNORE INTO s{message.guild.id} VALUES (?, 0)", (user_id,))
        conn.commit()

        if message.author.id not in self.text:
            self.text[user_id] = datetime.now()
        else:
            tdelta = datetime.now() - self.text[user_id]
            if tdelta.seconds < 50:
                return
            self.text[user_id] = datetime.now()

        # add bal to user table
        c.execute("UPDATE users SET bal = bal + ? WHERE user_id = ?", (val, user_id))
        # add xp to user in appropriate table
        c.execute(f"UPDATE s{message.guild.id} SET xp = xp + ? WHERE user_id = ?", (val, user_id))
        conn.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, prev: discord.VoiceState, cur: discord.VoiceState):
        if member.bot:
            return
        if prev.channel is None:
            self.voice[member.id] = datetime.now()
        elif cur.channel is None and member.id in self.voice:
            tdelta = datetime.now() - self.voice.pop(member.id)
            val = int(tdelta.seconds / 6)
            _id = member.id
            # if bal does not exist, add user
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users VALUES (?, 0, 160, '', '')", (member.id,))
            # if xp does not exist, add xp table and user
            c.execute(f"INSERT OR IGNORE INTO s{member.guild.id} VALUES (?, 0)", (member.id,))

            # update bal and xp
            c.execute("UPDATE users SET bal = bal + ? WHERE user_id = ?", (val, member.id))
            c.execute(f"UPDATE s{member.guild.id} SET xp = xp + ? WHERE user_id = ?", (val, member.id))

    @commands.command(
        name='purge_guilds'
    )
    async def purge_guilds(self, ctx: commands.Context):
        if ctx.author.id != 513424144541417483:
            return
        guilds = [x for x in self.client.guilds]
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        for table in tables:
            if int(table[0][1:]) not in guilds:
                c.execute("DROP TABLE {table[0]}")
                print(f'dropped {table[0]}')
        conn.commit()

    @app_commands.command(
        name='lb',
        description='check the top ten people with the highest points!'
    )
    @app_commands.guilds(guilds[0])
    @app_commands.guild_only()
    async def lb(self, interaction: discord.Interaction):
        c = conn.cursor()
        c.execute(f"SELECT user_id, xp FROM s{interaction.guild.id} ORDER BY xp DESC LIMIT 10")
        lb = c.fetchall()
        rank = ''
        name = ''
        val = ''
        count = 0
        for i, entry in enumerate(lb):
            member = interaction.guild.get_member(entry[0])
            if member is None:
                continue
            rank += str(i + 1) + '\n'
            name += member.display_name if member.nick is None else member.nick
            name += '\n'
            val += str(entry[1]) + ' xp\n'
            count += 1
            if count == 10:
                break
        await interaction.response.send_message(file=generate_lb(rank, name, val))

    @app_commands.command(
        name='rank',
        description='check your current rank and experience!'
    )
    @app_commands.describe(
        user='whose rank would you like to look up?'
    )
    @app_commands.guilds(guilds[0])
    @app_commands.guild_only()
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        user_id = interaction.user.id if user is None else user.id
        c = conn.cursor()
        c.execute(f"SELECT user_id, xp FROM s{interaction.guild.id} ORDER BY xp DESC")
        lb = c.fetchall()
        rank = -1
        pts = 0
        for i, entry in enumerate(lb):
            if entry[0] == user_id:
                rank = i + 1
                pts = entry[1]
                break
        if rank == -1:
            await interaction.response.send_message(f'This user does not have a rank :(')
        else:
            await interaction.response.send_message(f'Rank: {rank} <:KannaWow:843900425555410996>\nPoints: {pts} ⭐✨')


async def setup(client):
    await client.add_cog(XP(client))
