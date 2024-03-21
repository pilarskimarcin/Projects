from sys import stderr
from traceback import print_exception
from typing import List

import discord
from discord.ext import commands


def version_check() -> str:
    with open("Changelog.txt", "r") as f:
        lines: List[str] = f.readlines()
        i: int = lines.index("Current version:\n")
        return lines[i - 1].replace("v", "")


class SelfCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.rate_limit_flag: bool = False

    @commands.Cog.listener("on_ready")
    # When the bot is ready to use, it will display the message with its name and set activity to "watching the chat"
    async def confirm_logging_in(self):
        print('I am logged in as {0.user}'.format(self.bot))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.member)
    async def help(self, ctx: commands.context.Context):
        """
        A help command, listing all available commands
        """
        # TODO:
        #   change it to a group, so it can later be used "Wraith help <command>"
        # Non-breaking space - normal spaces and Tabs aren't working in an embed
        nbsp: str = "\xa0"
        # IMPORTANT - the help command is formatted this way, so it is shown properly on a phone - especially important
        # with the NBSPs - if the column of the character is higher than 81 (judged by the "seek name" explanation), it
        # will break into the next line without an NBSP
        help_msg: str = "**Moderation commands**\n" \
                        "`Wraith seek (<name>) (-all) (-roles)` - I will find the illiterate\n" \
                        f"{10 * nbsp}optional arguments:\n" \
                        f"{20 * nbsp}`-all` - doesn't matter when they joined\n" \
                        f"{20 * nbsp}`-roles` - what roles they DID take?\n" \
                        "`Wraith generate_kicks` - use after finding the guilty to prepare punishment\n" \
                        "`Wraith colour_fix` - check if everyone chose a colour\n" \
                        "`Wraith when <User_ID>` - see for how long they are staying here\n" \
                        "`Wraith roles` - look how much I need to remember for your server\n" \
                        "`Wraith add` - add more roles to those I track, for details, " \
                        "call `Wraith add help`\n" \
                        "\n**Commands about me**\n" \
                        "`Wraith help` - ...I think that's obvious, actually...\n" \
                        "`Wraith ping` - play ping pong\n" \
                        "`Wraith changelog` - see recent changes in the current version\n" \
                        "\n**Fun commands**\n" \
                        "`Wraith PraiseTheSun/Praise` - PRAISE THE SUN!\n" \
                        "`Wraith bearer` - Bearer- seek-\n" \
                        "`Wraith gif` - Look, I am the OwO now!\n" \
                        f"{10 * nbsp}AUTHOR does something:\n" \
                        f"{20 * nbsp}`anime scared`, `crab rave`,\n" \
                        f"{20 * nbsp}`creepy smile`, `depressed`,\n" \
                        f"{20 * nbsp}`emotional damage`, `general kenobi`,\n" \
                        f"{20 * nbsp}`hackerman`, `hang myself`, `head tilt`,\n" \
                        f"{20 * nbsp}`hello`, `hello there`, `hey hey`\n" \
                        f"{20 * nbsp}`hollow`, `katana attack`,\n" \
                        f"{20 * nbsp}`shoot myself`, `so uncivilised`,\n" \
                        f"{20 * nbsp}`subaru scared`, `what`\n" \
                        f"{10 * nbsp}AUTHOR interacts with PERSON:\n" \
                        f"{20 * nbsp}`banhammer`, `大丈夫`, `danganronpa`,\n" \
                        f"{20 * nbsp}`gundyr kick`, `hammer`, `kick`, `punch`,\n" \
                        f"{20 * nbsp}`re:zero pat`, `sorry`, `zhongli bonk`\n" \
                        f"{10 * nbsp}no message:\n" \
                        f"{20 * nbsp}`bears dance`, `echidna spin`, `glasses`,\n" \
                        f"{20 * nbsp}`jetstream sam`, `joker dance`,\n" \
                        f"{20 * nbsp}`my brain trembles`, `my source`, `sam`,\n" \
                        f"{20 * nbsp}`sunglasses`, `you\'re welcome`\n" \
                        f"{10 * nbsp}other gifs:\n" \
                        f"{20 * nbsp}`bye`, `emilia`, `fight`, `I have arrived`,\n" \
                        f"{20 * nbsp}`no memes in #general`"
        # If it's the owner, send him more commands privately
        if isinstance(ctx.channel, discord.DMChannel) and commands.is_owner():
            help_msg += "\n\nAdditional commands:\n" \
                        "`Wraith save_log` - save the discord.log to a new file\n" \
                        "`Wraith server_info <name>` - get basic info about the server\n" \
                        "`Wraith rate_limit` - set the rate_limit_flag to True"
        help_msg += f"\n{135 * nbsp}Version {version_check()}"
        # Creating an embed
        embed: discord.Embed = discord.Embed(description=help_msg)
        # Author's name is just so the description shows up nicely
        embed.set_author(name="Guide", icon_url=self.bot.user.avatar.url)
        try:
            await ctx.send(embed=embed)
        # Might not have permissions to send an embed
        except discord.Forbidden:
            help_msg = "\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\n" \
                       "**__Guide__**\n" + help_msg + \
                       "\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_"
            if len(help_msg) <= 2000:
                await ctx.send(help_msg)
            else:
                help_new = [help_msg]
                while max([len(el) for el in help_new]) > 2000:
                    help_new2 = help_new[:]
                    for number in range(len(help_new2)):
                        part = help_new2[number]
                        if len(part) <= 2000:
                            continue
                        new_part: str = part[2000:]
                        part = part[:2000]
                        i: int = part.index("\n", -100)
                        new_part = part[i + 1:] + new_part
                        part = part[:i + 1]
                        help_new[number] = part
                        help_new.insert(number + 1, new_part)
                for help_part in help_new:
                    await ctx.send(help_part)

    @commands.command()
    @commands.cooldown(1, 4, commands.BucketType.member)
    async def ping(self, ctx: commands.context.Context):
        """
        A generic ping command
        """
        await ctx.send(f"{ctx.author.mention} pong")

    # Not needed any longer, was used when a faulty hosting service was used with a lot of rate-limit problems
    # # Manual "rate-limit"
    # @commands.command()
    # @commands.is_owner()
    # async def rate_limit(self, ctx: commands.context.Context):
    #     self.rate_limit_flag = True

    # # To send a message to the owner when the rate limit happened
    # @commands.Cog.listener("on_message")
    # async def checking_if_bot_was_rate_limited(self, message: discord.Message):
    #     if message.content == "Wraith rate_limit":
    #         return
    #     if self.rate_limit_flag:
    #         try:
    #             self.rate_limit_flag = False
    #             await self.bot.application.owner.send("I have been rate-limited")
    #         except discord.Forbidden:  # If the owner is not in this server
    #             return

    @commands.Cog.listener("on_command_error")
    async def error(self, ctx: commands.Context, exception: Exception):
        """
        A listener handling errors
        """
        print('Ignoring exception in command {}:'.format(ctx.command), file=stderr)
        print_exception(type(exception), exception, exception.__traceback__, file=stderr)
        if isinstance(exception, commands.errors.CommandNotFound):
            # Try to find a gif with that name (maybe someone forgot to add "gif" before the name)
            try:
                await self.bot.get_command("gif")(ctx, args=ctx.message.content.replace(ctx.clean_prefix, ""))
            except Exception as e:
                print_exception(type(e), e, e.__traceback__, file=stderr)
            return
        elif isinstance(exception, commands.CommandOnCooldown):
            await ctx.send(f"No way I'm gonna work *that* fast", delete_after=5)
            return
        elif isinstance(exception, commands.errors.CheckFailure):
            # If the check failed, it means it was a moderation command, so 2 scenarios:
            # 1. Trying to do it outside any server
            if ctx.guild is None:
                await ctx.send("Moderating sneakily? No, go on the server and do it there")
                return
            # 2. If done on the server, the user isn't considered staff by the check
            else:
                await ctx.send("Put these foolish ambitions to rest, no one has granted you the rank of Master",
                               delete_after=7)
                return
        await ctx.send(f"Unknown error, notify my master, {self.bot.application.owner.name}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def changelog(self, ctx: commands.Context):
        with open("Changelog.txt", "r") as f:
            lines: List[str] = f.readlines()
            i: int = lines.index("Current version:\n")
            text: str = "".join(lines[i:])
        await ctx.send(text)
