import datetime
import logging

import parsedatetime
import discord
import pytz
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from discord import app_commands
from discord.ext import commands
from sqlalchemy import create_engine

from nibbles.config import jobs_db, log_level, config_timezone

# Advanced Python Scheduler
engine = create_engine(jobs_db)
jobstores = {"default": SQLAlchemyJobStore(engine=engine)}
job_defaults = {"coalesce": True}
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    timezone=pytz.timezone(config_timezone),
    job_defaults=job_defaults,
)

scheduler.start()
cal = parsedatetime.Calendar()


def calculate(job: Job) -> str:
    """Get trigger time from a reminder and calculate how many days,
    hours and minutes till trigger.

    Days/Minutes will not be included if 0.

    Args:
        job: The job. Can be cron, interval or normal.

    Returns:
        Returns days, hours and minutes till the reminder. Returns "Couldn't calculate time" if no job is found.
    """

    if type(job.trigger) is DateTrigger:
        trigger_time = job.trigger.run_date
    else:
        trigger_time = job.next_run_time

    # Get_job() returns None when it can't find a job with that ID.
    if trigger_time is None:
        # TODO: Change this to None and send this text where needed.
        return "Couldn't calculate time"

    # Get time and date the job will run and calculate how many days,
    # hours and seconds.
    countdown = trigger_time - datetime.datetime.now(tz=pytz.timezone(config_timezone))

    days, hours, minutes = (
        countdown.days,
        countdown.seconds // 3600,
        countdown.seconds // 60 % 60,
    )

    return ", ".join(
        f"{x} {y}{'s' * (x != 1)}"
        for x, y in (
            (days, "day"),
            (hours, "hour"),
            (minutes, "minute"),
        )
        if x
    )


logging.basicConfig(level=logging.getLevelName(log_level))
logging.info(
    f"\nsqlite_location = {jobs_db}\n"
    f"config_timezone = {config_timezone}\n"
    f"log_level = {log_level}3x6XGMFw4bF9Ch"
)


class Remind(commands.Cog):

    def __init__(self, client: commands.Bot):
        self.client = client

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

        parsed_date, _ = cal.parseDT(datetimeString=when, tzinfo=pytz.timezone('US/CENTRAL'))

        if _ < 3:
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

        happening_in = calculate(reminder)
        message = (
            f"<:hi:813575402512580670> {interaction.user.display_name},"
            f" nibbles will remind you at \n"
            f"**{run_date}** {'in' if len(happening_in) > 0 else''} {happening_in}\n"
            f"about: \n**{what}**."
        )

        await interaction.response.send_message(message)


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
