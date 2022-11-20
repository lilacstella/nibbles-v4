import discord
from discord import app_commands
from discord.ext import commands

from nibbles.config import servers_db as conn


class AddChannel(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:NibblesYes:869957381134647316>", style=discord.ButtonStyle.primary,
                         custom_id="add_channel")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.permissions.manage_guild:
            await interaction.response.defer()
            return
        c = conn.cursor()
        c.execute("UPDATE servers SET birthday = ? WHERE guild = ?", (interaction.channel_id, interaction.guild_id))
        conn.commit()
        await interaction.response.send_message(f"Announcement channel set to {interaction.channel.mention}")


class RemoveChannel(discord.ui.Button):
    def __init__(self):
        super().__init__(emoji="<:NibblesNo:869957380924928050>", style=discord.ButtonStyle.danger,
                         custom_id="remove_channel")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.permissions.manage_guild:
            await interaction.response.defer()
            return
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

    async def cog_unload(self):
        self.client.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)
        self.birthday_check.cancel()

    async def settings(self, interaction: discord.Interaction, message: discord.Message) -> None:
        if not interaction.permissions.manage_guild:
            await interaction.response.send_message("You do not have permissions to change this!")
            return
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


async def setup(client):
    await client.add_cog(ServerConfig(client))
