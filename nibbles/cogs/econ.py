import asyncio
import secrets

import discord
from discord.ext import commands

from nibbles.config import guilds
from nibbles.config import user_db as conn


class Econ(commands.Cog):

    def __init__(self, client):
        self.spun_today = {}
        self.client = client

    @commands.hybrid_command(
        name="spin",
        description='spin the wheel of fortune once a day!',
        with_app_command=True,
        aliases=['wheel'],
        guilds=guilds
    )
    async def wheel(self, ctx: commands.Context):
        if ctx.author.id in self.spun_today:
            await ctx.send('You have already spun your wheel today!')
        else:
            self.spun_today[ctx.author.id] = True
            await self.gamble_wheel(ctx.author, ctx)

    async def gamble_wheel(self, author, channel):
        c = conn.cursor()
        c.execute(f"INSERT OR IGNORE INTO users VALUES (?, 0, 160, '', '')", (author.id,))
        c.execute('SELECT bal FROM users WHERE user_id = ?', (author.id,))
        bal = c.fetchone()[0]

        embed = discord.Embed(title="**SPINNING**", colour=discord.Colour(secrets.randbelow(0xFFFFFF)))
        embed.set_image(url="https://i.pinimg.com/originals/94/cc/d5/94ccd56f2a24d1eb9486d86fcee0b3b1.gif")
        embed.set_thumbnail(url=author.avatar.url
        if not hasattr(author, 'guild_avatar') or
           author.guild_avatar is None else
        author.guild_avatar.url)
        embed.set_author(name=str(author))
        embed.set_footer(text="best of luck!", icon_url="https://cdn.discordapp.com/emojis/948031133281562724.webp")

        msg = await channel.send(content="Spinning the Wheel of Fortune", embed=embed)

        if secrets.randbelow(100) == 0:
            result = 10000
        else:
            result = secrets.randbelow(2100 - 700) + 701

        embed = discord.Embed(title="**REWARDS**", colour=discord.Colour(secrets.randbelow(0xFFFFFF + 1)))
        embed.set_thumbnail(url=author.avatar.url
        if not hasattr(author, 'guild_avatar') or author.guild_avatar is None else author.guild_avatar.url)
        embed.set_author(name=str(author))
        embed.add_field(name="Prize", value=str(result) + " nom noms", inline=False)
        embed.add_field(name="Current Balance", value=str(bal + result), inline=False)
        embed.set_footer(text='use .help to find out what nom noms do!')

        await asyncio.sleep(4)
        c.execute('UPDATE users SET bal = bal + ? WHERE user_id = ?', (result, author.id))
        conn.commit()
        await msg.edit(content='Wheel of Fortune Results', embed=embed)


async def setup(client):
    await client.add_cog(Econ(client))
