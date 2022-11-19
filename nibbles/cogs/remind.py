from datetime import datetime, timedelta, date

import dateparser
import discord
import pytz

from discord import app_commands
from discord.ext import commands

from nibbles.config import jobs_db, log_level, config_timezone, user_db, servers_db

import pytz
import logging
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine

# Advanced Python Scheduler
engine = create_engine(jobs_db)

logging.basicConfig(level=logging.getLevelName(log_level))
logging.info(
    f"\nsqlite_location = {jobs_db}\n"
    f"config_timezone = {config_timezone}\n"
    f"log_level = {log_level}3x6XGMFw4bF9Ch"
)

jobstores = {"default": SQLAlchemyJobStore(engine=engine)}
job_defaults = {"coalesce": True}
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=pytz.timezone(config_timezone),
    job_defaults=job_defaults,
)

scheduler.start()


class CancelRemind(discord.ui.Button):
    def __init__(self, job_id, view: discord.ui.View):
        self.job_id = job_id
        super().__init__(
            style=discord.ButtonStyle.danger,
            custom_id="cancel",
            emoji=discord.PartialEmoji.from_str('<:NibblesNo:869957380924928050>')
        )

    async def callback(self, interaction: discord.Interaction):
        _job = scheduler.get_job(self.job_id)
        if not hasattr(_job, 'kwargs') or interaction.user.id != _job.kwargs['author_id']:
            await interaction.response.defer()
            return
        scheduler.remove_job(self.job_id)
        self.view.clear_items()
        await interaction.response.edit_message(content="this reminder was cancelled", view=self.view)


class CancelView(discord.ui.View):
    def __init__(self, job_id, timeout=1200):
        super().__init__(timeout=timeout)
        self.add_item(CancelRemind(job_id, self))


class Remind(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

    def birthday_start(self):
        # set time zone
        tz = pytz.timezone(config_timezone)
        # Get today's date in the current time zone (i.e local time)
        # note time() without arguments will result to midnight
        midnight_local = datetime.combine(date.today(), datetime.min.time())
        # midnight_local = datetime.now() + timedelta(seconds=15) # test start in 15s
        # convert this midnight datetime to the midnight datetime
        # in the given time zone. In this case autralia time zone
        midnight = tz.localize(midnight_local)
        scheduler.add_job(
            birthday_check,
            'interval',
            hours=24,
            start_date=midnight,
            timezone=config_timezone
        )
        print(midnight)

    @app_commands.command(
        name="remindme",
        description="Set a reminder for future you!"
    )
    @app_commands.describe(
        what="What do you want to be reminded about?",
        when="When do you want to be reminded?"
    )
    async def command_add(
            self,
            interaction: discord.Interaction,
            what: str,
            when: str
    ):
        """Add a new reminder. You can add a date and message.

        Args:
            interaction: Context of the slash command. Contains the guild, author and message and more.
            message_date: The parsed date and time when you want to get reminded.
            when: The message the bot should write when the reminder is triggered.
            different_channel: The channel the reminder should be sent to.
        """
        try:
            parsed_date = dateparser.parse(
                when,
                settings={
                    "TIMEZONE": config_timezone,
                    "TO_TIMEZONE": config_timezone,
                    'PREFER_DAY_OF_MONTH': 'first',
                    'RETURN_AS_TIMEZONE_AWARE': True
                    # 'PREFER_DATES_FROM': 'current_period'
                },
            )
        except dateparser.SettingValidationError as e:
            return await interaction.response.send_message(f"Timezone is possible wrong?: {e}", ephemeral=True)
        except ValueError as e:
            return await interaction.response.send_message(
                f"Failed to parse date. Unknown language: {e}", ephemeral=True
            )
        if not parsed_date:
            return await interaction.response.send_message("Could not parse the date.", ephemeral=True)

        run_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        try:
            reminder = scheduler.add_job(
                send_to_discord,
                run_date=run_date,
                kwargs={
                    "channel_id": interaction.channel_id,
                    "message": what,
                    "author_id": interaction.user.id,
                },
            )
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        happening_in = parsed_date.timestamp()
        message = (
            f"<:hi:813575402512580670> {interaction.user.display_name},"
            f" nibbles will remind you at \n"
            f"**<t:{happening_in:.0f}:F>** <t:{happening_in:.0f}:R>\n"
            f"about: \n**{what}**."
        )

        await interaction.response.send_message(message, view=CancelView(reminder.id))


async def setup(client):
    global bot
    bot = client
    await client.add_cog(Remind(client))


async def send_to_discord(channel_id: int, message: str, author_id: int):
    """Send a message to Discord.

    Args:
        channel_id: The Discord channel ID.
        message: The message.
        author_id: User we should ping.
    """

    channel = bot.get_channel(channel_id)
    if channel is None:
        print(author_id, message, 'unable to be sent to channel')
        await bot.get_user(author_id).send(f"hi <@{author_id}> you told me to remind you {message} ")
    else:
        await channel.send(f"hi <@{author_id}> you told me to remind you {message}")


async def birthday_channels():
    def _retrieve_subscriptions():
        c = servers_db.cursor()
        c.execute(f'SELECT birthday, guild FROM servers')
        arr = c.fetchall()
        arr = list(filter(lambda a: a[0] != -1, arr))
        return [temp for temp in arr if any([x.id == temp[1] for x in bot.guilds])]

    today = datetime.now().strftime("%m/%d")
    birthdays = []
    cursor = user_db.cursor()
    cursor.execute("SELECT user_id FROM users WHERE birthday = ?", (today,))
    birthday_ppl = cursor.fetchall()
    for birthday_boi in birthday_ppl:
        channels = []
        for ch_id in _retrieve_subscriptions():
            try:
                channel = bot.get_channel(ch_id[0])
            except (discord.Forbidden, discord.NotFound):
                continue
            user = bot.get_user(birthday_boi[0])
            if user in channel.members and channel.guild.me.guild_permissions.send_messages:
                channels.append(channel)
        birthdays.append((birthday_boi[0], channels))
    return birthdays


async def birthday(user, channels):
    # function called for every user's birthday
    if len(channels) == 0:
        return
    mention = channels[0].guild.get_member(user).mention
    for channel in channels:
        await channel.send(f"Happy birthday to {mention}!!! "
                           f"<:NibblesCheer:869948008115109928><:NibblesCheer:869948008115109928>")


async def birthday_check():
    for bd in await birthday_channels():
        await birthday(*bd)