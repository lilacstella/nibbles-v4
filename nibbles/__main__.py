import discord
from discord.ext import commands

from nibbles.config import guilds, discord_token

"""
Define Bot Attributes
"""

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='',
                         intents=discord.Intents(guilds=True, members=True, messages=True),
                         case_insensitive=True)
        self.synced = False

    async def on_ready(self):
        await self.load_extension('nibbles.cogs.misc')
        await self.load_extension('nibbles.cogs.econ')
        await self.load_extension('nibbles.cogs.todo')
        await self.wait_until_ready()

        # if not self.synced:
        #     print(await self.tree.sync())
        #     for _id in guilds:
        #         await self.tree.sync(guild=_id)
        #     self.synced = True
        print("bot online")


client = Bot()
# econ.init_db()

"""
Register Discord Bot Commands
"""

# @app_commands.checks.cooldown(3, 5 * 60)
# @reg.command(
#     name="register",
#     description="register your information here",
#     guilds=guild_ids
# )
# @app_commands.describe(
#     name='please enter your full name/names you go by',
#     grad_year='your graduation year (yyyy)',
#     email='TAMU email'
# )
# async def register(
#         interaction: discord.Interaction, name: str, grad_year: int, email: str
# ):
#     try:
#         msg = backend.register(
#             name, grad_year, email, interaction.user.id, interaction.user.name
#         )
#     except:
#         await client.get_channel(1014740464601153536) \
#             .send(f"{interaction.user.mention} registration attempt, update token")
#         msg = "The verification code failed to send, an officer has been notified and will contact you soon"
#     await interaction.response.send_message(msg, ephemeral=True)

@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    if ctx.valid:
        await client.process_commands(message)

client.run(discord_token)