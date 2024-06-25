import asyncio
import contextlib
import sys
from typing import Any

import discord
from discord.ext import commands
from loguru import logger

from tux.cog_loader import CogLoader
from tux.database.client import db
from tux.utils.activities import ActivityChanger
from tux.utils.console import Console
from tux.utils.constants import Constants as CONST
from tux.utils.sentry import setup_sentry

logger.remove()
log_format = CONST.LOG_FORMAT_OPTIONS[CONST.LOG_FORMAT]
logger.add(sys.stdout, format=log_format, colorize=True, level=CONST.LOG_LEVEL)
logger.add("logs/tux.log", format=log_format, colorize=True, level="DEBUG")


class TuxBot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.activity_changer = ActivityChanger(self)
        self.setup_task = asyncio.create_task(self.setup())
        self.is_shutting_down = False

    async def setup(self) -> None:
        """
        Sets up the bot by connecting to the database and loading cogs.
        """
        try:
            # Connect to Prisma
            await db.connect()
            logger.info("Database connection established.")

        except Exception as e:
            logger.error(f"An error occurred while connecting to the database: {e}")
            return

        # Load cogs via CogLoader
        await self.load_cogs()

    async def load_cogs(self) -> None:
        """
        Loads cogs by calling the setup method of CogLoader.
        """

        await CogLoader.setup(self)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Executes actions when the bot is ready, such as connecting to Discord and running tasks.
        """

        if not self.setup_task.done():
            await self.setup_task

        logger.info(f"{self.user} has connected to Discord!")

        activity_task = asyncio.create_task(self.activity_changer.run())

        await asyncio.gather(activity_task)

    @commands.Cog.listener()
    async def on_disconnect(self) -> None:
        """
        Executes actions when the bot disconnects from Discord, such as closing the database connection.
        """
        logger.warning("Bot has disconnected from Discord.")

    async def shutdown(self):
        if self.is_shutting_down:
            logger.info("Shutdown already in progress. Exiting...")
            return
        self.is_shutting_down = True

        logger.info("Shutting down...")

        await self.close()

        # Cancel all tasks except the current one
        if tasks := [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]:
            logger.info(f"Cancelling {len(tasks)} outstanding tasks")
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("All tasks cancelled.")

        try:
            logger.info("Closing database connections...")
            await db.disconnect()

        except Exception as e:
            logger.error(f"Error during database disconnection: {e}")

        logger.info("Shutdown complete.")


async def main() -> None:
    prefix = CONST.DEV_PREFIX if CONST.DEV == "True" else CONST.PROD_PREFIX
    token = CONST.DEV_TOKEN if CONST.DEV == "True" else CONST.PROD_TOKEN
    intents = discord.Intents.all()
    bot = TuxBot(command_prefix=prefix, intents=intents)

    # Initialize the console and console task
    console = None
    console_task = None

    # Setup Sentry for error tracking and reporting
    setup_sentry()

    try:
        console = Console(bot)
        console_task = asyncio.create_task(console.run_console())

        # Start the bot and reconnect on disconnection
        await bot.start(token=token, reconnect=True)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, shutting down.")

    finally:
        logger.info("Closing resources.")
        await bot.shutdown()

        # Cancel the console task if it's still running
        if console_task is not None and not console_task.done():
            console_task.cancel()
            # Suppress the CancelledError exception
            with contextlib.suppress(asyncio.CancelledError):
                await console_task

    logger.info("Bot shutdown complete.")


if __name__ == "__main__":
    try:
        # Run the bot using asyncio
        asyncio.run(main())

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt gracefully
        logger.info("Exiting gracefully.")
