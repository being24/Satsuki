import logging
import logging.handlers
import pathlib
import traceback
from os import getenv

import discord
from discord.ext import commands
from discord_sentry_reporting import use_sentry
from dotenv import load_dotenv
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(
            command_prefix=command_prefix,
            help_command=None,
            intents=intents,
        )

    async def setup_hook(self) -> None:
        for cog_path in current_path.glob("cogs/*.py"):
            try:
                await self.load_extension(f"cogs.{cog_path.stem}")
                print(f"Loaded: {cog_path.stem}")
            except Exception:
                print(f"Failed to load: {cog_path.stem}")
                traceback.print_exc()

    async def on_ready(self):
        print("-----")
        print("Logged in as")
        if self.user:
            print(self.user.name)
            print(self.user.id)
        print("------")
        logger.warning("rebooted")
        await bot.change_presence(activity=discord.Game(name="info bot Satsuki"))


if __name__ == "__main__":
    dotenv_path = pathlib.Path(__file__).parents[0] / ".env"
    load_dotenv(dotenv_path)

    token = getenv("DISCORD_BOT_TOKEN")
    dsn = getenv("SENTRY_DSN")

    logfile_path = pathlib.Path(__file__).parents[0] / "log" / "discord.log"

    if token is None:
        raise FileNotFoundError("Token not found error!")

    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    handler = logging.handlers.RotatingFileHandler(
        filename=logfile_path,
        encoding="utf-8",
        maxBytes=32 * 1024,  # 32 KiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    logger.addHandler(handler)

    current_path = pathlib.Path(__file__).parents[0]

    intents = discord.Intents.default()
    intents.members = True
    intents.typing = False
    intents.integrations = True
    intents.message_content = True

    bot = MyBot(command_prefix=commands.when_mentioned_or("/"))

    if dsn is not None:
        sentry_logging = LoggingIntegration(
            level=logging.WARNING,  # Capture info and above as breadcrumbs
            event_level=logging.WARNING,  # Send errors as events
        )

        use_sentry(bot, dsn=dsn, integrations=[AioHttpIntegration(), sentry_logging])

    bot.run(
        token, log_handler=handler, log_formatter=formatter, log_level=logging.WARNING
    )
