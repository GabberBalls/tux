import discord
from discord.ext import commands
from loguru import logger

from tux.utils.constants import Constants as CONST


class Tickets(commands.Cog):
    """
        A cog that manages tickets.

        Attributes
        ----------
        bot : commands.Bot
            The bot instance.
        base_vc_name : str
            The base name for temporary voice channels.
        """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.base_ticket_name: str = "/ticket/"

    @commands.hybrid_command(
        name="ticket",
        usage="$ticket [reason]",
    )
    async def ticket(self, ctx: commands.Context, reason: str) -> None:



    @staticmethod
    async def try_assign_role(member: discord.Member, role: discord.Role) -> None:
        """
        Assign a role to a member.

        Parameters
        ----------
        member : discord.Member
            The member to assign the role to.
        role : discord.Role
            The role to assign.
        """

        try:

            await member.add_roles(role)

        except Exception as error:
            logger.error(f"Failed to assign role {role.name} to {member}: {error}")



