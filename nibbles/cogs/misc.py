import asyncio
import secrets
import threading
from datetime import datetime

import discord
from discord.ext import commands


from nibbles.config import guilds

"""Reroll Button and View"""


class Reroll(discord.ui.Button):
    def __init__(self, options: list, crossed: list, view: discord.ui.View):
        super().__init__(style=discord.ButtonStyle.primary, custom_id="reroll", emoji="🔁")
        self.crossed = crossed
        self.options = options

        # self.response = None
        label = ""
        for choice in options: label += choice.strip() + ","
        label = label[:-1]
        self.label = label if label != '' else None

    async def callback(self, interaction: discord.Interaction):
        if self.label is None:
            await interaction.response.defer()
            return

        chosen = secrets.choice(self.options)

        self.options.remove(chosen)
        selected = chosen
        for _item in self.crossed:
            selected += f" ~~{_item}~~"
        self.crossed.append(chosen)
        choice = [f'Nibbles thinks  __{selected}__  is the right option!',
                  f'Of course __{selected}__ is the way to go!',
                  f"Nibbles thinks __{selected}__ is da best. It's tasty after all!",
                  f'After consulting my degree in Abstract Mathematics, Nibbles thinks __{selected}__ is the right choice.',
                  f"Nibbles likes __{selected}__ because it has the most nom noms"]
        label = ""
        for _cur in self.options: label += _cur.strip() + ","
        label = label[:-1]
        self.label = label
        await interaction.response.edit_message(content=secrets.choice(choice), view=self.view)


class RerollView(discord.ui.View):
    def __init__(self, options: list, crossed: list, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(Reroll(options, crossed, self))


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.hybrid_command(
        name="choose",
        description="nibbles helps make your life decisions for you",
        guilds=guilds
    )
    @discord.app_commands.describe(
        options='what would you like nibbles to choose from (options seperated by commas)'
    )
    async def choose(self, ctx: commands.Context, options: str):
        """let nibbles help you choose something"""
        choices = [x.strip() for x in options.split(',') if x != '']
        chosen = secrets.choice(choices)
        choices.remove(chosen)
        view = RerollView(choices, [chosen])
        chosen = [f'Nibbles thinks  __{chosen}__  is the right option!', f'Of course __{chosen}__ is the way to go!',
                  f"Nibbles thinks __{chosen}__ is da best. It's tasty after all!",
                  f'After consulting my degree in Abstract Mathematics, Nibbles thinks __{chosen}__ is the right choice.',
                  f"Nibbles likes __{chosen}__ because it has the most nom noms"]

        await ctx.send(secrets.choice(chosen), view=view)

    @commands.hybrid_command(
        name="size",
        description="find the number of human members",
        guilds=guilds
    )
    async def size(self, ctx: commands.Context):
        if ctx.guild is None:
            await ctx.send(f"There is one human here and that is you")
            return
        count = 0
        for member in ctx.guild.members:
            if not member.bot:
                count += 1
        await ctx.send(f"There are {count} humans in the server.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.client.user.mentioned_in(message) and not message.mention_everyone:
            eight_ball = [
                'Nibbles agree.', 'Yesssu!', 'Yes yes.', 'Nibbles approve.',
                'You can bet nom noms on it.', 'Nibbles thinks that is correct.',
                'Most likely.', 'Good good.', 'Ooooo wats dat?',
                'My nom noms said yes.', 'Huh? What did you say?.',
                'I\'m sleepy... ask later.', 'Its a secret hehe.',
                'Nibbles thinks that is wrong.', 'My nom noms said no.',
                'Nibbles disagree.', 'Noooooo!', 'That is incorrect.'
            ]
            await message.channel.send(secrets.choice(eight_ball))


async def setup(client):
    await client.add_cog(Misc(client))
