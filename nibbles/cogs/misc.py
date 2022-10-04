import secrets

import discord
from discord.ext import commands

from nibbles.config import guilds

class Reroll(discord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.response = None
        label = ""
        for choice in options: label += choice.strip() + ","
        label = label[:-1]
        self.reroll.label = label

    @discord.ui.button(
        style=discord.ButtonStyle.primary, custom_id="reroll", emoji="🔁"
    )
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if button.label is None:
            await interaction.response.defer()
            return
        options = button.label.split(',')
        chosen = secrets.choice(options)
        options.remove(chosen)
        selected = f'__{chosen.strip()}__'
        choice = [f'Nibbles thinks  {selected}  is the right option!', f'Why of course {selected} is the way to go!',
                  f"Nibbles thinks {selected} is da best. It's tasty after all!",
                  f'After consulting my degree in Mathematics, Nibbles thinks {selected} is the right choice.',
                  f"Nibbles likes {selected} because it has the most nom noms"]
        label = ""
        for _cur in options: label += _cur.strip() + ","
        label = label[:-1]
        button.label = label
        await interaction.response.edit_message(content=secrets.choice(choice), view=self)


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
        choices = options.split(',')
        chosen = secrets.choice(choices)
        choices.remove(chosen)
        selected = f'__{chosen.strip()}__'
        choice = [f'Nibbles thinks  {selected}  is the right option!', f'Of course {selected} is the way to go!',
                  f"Nibbles thinks {selected} is da best. It's tasty after all!",
                  f'After consulting my degree in Mathematics, Nibbles thinks {selected} is the right choice.',
                  f"Nibbles likes {selected} because it has the most nom noms"]
        await ctx.send(secrets.choice(choice), view=Reroll(choices))

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
