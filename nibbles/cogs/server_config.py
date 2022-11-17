from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from nibbles.config import servers_db as conn
from nibbles.config import user_db

class AddChannel(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:NibblesYes:869957381134647316>", style=discord.ButtonStyle.primary,
                         custom_id="add_channel")

    async def callback(self, interaction: discord.Interaction):
        c = conn.cursor()
        c.execute("UPDATE servers SET birthday = ? WHERE guild = ?", (interaction.channel_id, interaction.guild_id))
        conn.commit()
        await interaction.response.send_message(f"Announcement channel set to {interaction.channel.mention}")


class RemoveChannel(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:NibblesNo:869957380924928050>", style=discord.ButtonStyle.danger,
                         custom_id="remove_channel")

    async def callback(self, interaction: discord.Interaction):
        c = conn.cursor()
        c.execute("UPDATE servers SET birthday = -1 WHERE guild = ?", (interaction.guild_id,))
        conn.commit()
        await interaction.response.send_message(f"Announcement channel has been removed")


class SelectChannelsView(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(AddChannel())
        self.add_item(RemoveChannel())


class ServerConfig(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.ctx_menu = app_commands.ContextMenu(name="Server Configuration", callback=self.settings)
        self.client.tree.add_command(self.ctx_menu)

    @discord.ext.tasks.loop(hours=24)
    async def birthday_check(self):
        for birthday in await self.birthday_channels():
            await self.birthday(*birthday)

    async def cog_unload(self):
        self.client.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        self.birthday_check.cancel()

    @app_commands.checks.has_permissions(manage_guild=True)
    async def settings(self, interaction: discord.Interaction, message: discord.Message) -> None:
        c = conn.cursor()
        c.execute("SELECT count(*) FROM servers WHERE guild = ?", (message.guild.id,))
        exists = c.fetchone()[0]
        if exists == 0:
            c.execute(f"INSERT INTO servers VALUES (?, -1, -1, -1, -1, -1, -1, 0, '.')", (message.guild.id,))
            conn.commit()

        c.execute("SELECT birthday FROM servers WHERE guild = ?", (message.guild.id,))
        birthday_channel = c.fetchone()[0]
        desc = ""
        if birthday_channel == -1:
            desc = "There has not been a set channel for announcements yet. " \
                   "Click <:NibblesYes:869957381134647316> to add the current channel as the announcement channel. "
        else:
            channel = self.client.get_channel(birthday_channel)
            desc = f"Current channel for announcement messages: \n" \
                   f"{'CANNOT ACCESS' if channel is None else channel.mention}"

        embed = discord.Embed(title="Server Settings", description=desc)

        msg = await interaction.response.send_message(embed=embed, view=SelectChannelsView())

    async def birthday_channels(self):
        today = datetime.now().strftime("%m/%d")
        birthdays = []
        cursor = user_db.cursor()
        cursor.execute("SELECT user_id FROM users WHERE birthday = ?", (today,))
        birthday_ppl = cursor.fetchall()
        for birthday_boi in birthday_ppl:
            channels = []
            for ch_id in self._retrieve_subscriptions('birthday'):
                try:
                    channel = await self.client.get_channel(ch_id[0])
                except (discord.Forbidden, discord.NotFound):
                    continue
                user = self.client.get_user(birthday_boi[0])
                if user in channel.members and channel.guild.me.guild_permissions.send_messages:
                    channels.append(channel)
            birthdays.append((birthday_boi[0], channels))
        return birthdays

    async def birthday(self, user, channels):
        # function called for every user's birthday
        if len(channels) == 0:
            return
        mention = channels[0].guild.get_member(user).mention
        for channel in channels:
            await channel.send(f"Happy birthday to {mention}!!! "
                               f"<:NibblesCheer:869948008115109928><:NibblesCheer:869948008115109928>")


async def setup(client):
    await client.add_cog(ServerConfig(client))
