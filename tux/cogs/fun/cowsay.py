import discord
from discord.ext import commands
from loguru import logger

from tux.utils.embeds import EmbedCreator




class Cowsay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="cowsay",
        aliases=["cow"],
        usage="$cowsay <subcommand>",
    )
    @commands.guild_only()
    async def cowsay(self, ctx: commands.Context[commands.Bot], msg: str | None = None) -> None:
        """
        Cowsay in tux.


        Parameters
        ----------
        ctx: commands.Context[commands.Bot]
        The context of the command.
        msg: str | None
        The message to be relayed through the cow.


        """


        if msg:
            await self.usermsg(ctx, msg)
        else:
            await ctx.send_help("cowsay")


    @cowsay.command(
        name="usrmsg",
        aliases=["usrmsg","u","msg","m"],
        usage="$cowsay usrmsg <message>",
    )

    @commands.guild_only()
    async def usermsg(self, ctx: commands.Context[commands.Bot], msg: str) -> None:
        """
                Relays a user-provided message through a cow.

                Parameters
                ----------
                ctx : commands.Context[commands.Bot]
                    The context object for the command.

                """
        embed = self.send_cow_message(ctx, msg)


        await ctx.reply(embed=embed)


    async def send_cow_message(self ,ctx: commands.Context[commands.Bot], msg: str, quote: bool) -> discord.Embed:
        if quote:
            #TODO: quote logic, probably consult some kind of API







