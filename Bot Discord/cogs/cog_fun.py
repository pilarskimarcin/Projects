import random
from typing import Dict, List, Tuple

import discord
from discord.ext import commands


async def embed_sending(ctx: commands.Context, embed: discord.Embed, text: str = ""):
    """
    Function for sending an embed.

    :param ctx: context of the command call
    :param embed: the created embed
    :param text: text of the embed
    """
    embed.set_author(name=text, icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions(replied_user=False),
                   reference=ctx.message.reference)


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.k: int = 0
        self.gif_dict: Dict[str, Tuple[str, str]] = {
            # AUTHOR does something - gifs to convey emotions or say something
            "anime scared": ("https://media.tenor.com/TRPmLNKPbssAAAAS/anime-scared.gif", "AUTHOR is terrifed..."),
            "crab rave": ("https://media.tenor.com/CAPUr9jUMeQAAAAd/crab.gif", "AUTHOR is vibing 🦀"),
            "creepy smile": ("https://media.tenor.com/rtjjRa8R4u4AAAAC/tanya-smile.gif", "AUTHOR smiles..."),
            "depressed": ("https://media.tenor.com/vX3EkyCqr7YAAAAd/hollow-ds.gif", "AUTHOR is depressed..."),
            "emotional damage": ("https://media.tenor.com/K9-SqJMNjkEAAAAS/emotional-damage.gif", "AUTHOR says"),
            "general kenobi": (
                "https://media.tenor.com/L5n55GiSbx4AAAAd/general-kenobi-turn-around.gif", "AUTHOR says"),
            "hackerman": ("https://media.tenor.com/TbTe1Nc6j34AAAAC/hacker-hackerman.gif", "AUTHOR is a..."),
            "hang myself": ("https://media.tenor.com/p-IBe7DpJ5UAAAAC/tf2-spy.gif", "AUTHOR hanged themselves..."),
            "head tilt": ("https://media.tenor.com/rAH8nVxyXxsAAAAC/pet-head.gif", "AUTHOR is very confused..."),
            "hello": ("https://media.tenor.com/MBiYi5Tc5HgAAAAC/hello-grand-inquisitor.gif", "AUTHOR says"),
            "hello there": ("https://media.tenor.com/6us3et_6HDoAAAAC/hello-there-hi-there.gif", "AUTHOR says"),
            "hey hey": ("https://media.tenor.com/0wIFfaw9T9kAAAAC/yey-hey-kaguya-sama-love-is-war-s2.gif",
                        "AUTHOR says"),
            "hollow": ("https://media.tenor.com/vX3EkyCqr7YAAAAd/hollow-ds.gif", "AUTHOR is now Hollow"),
            "katana attack": ("https://media.tenor.com/CGFmiEU2y6IAAAAS/zenitsu-zenitsu-agatsuma.gif",
                              "AUTHOR attacks!"),
            "shoot myself": ("https://media.tenor.com/20YFPIkutx0AAAAC/anime.gif", "AUTHOR shot themselves..."),
            "so uncivilised": ("https://media.tenor.com/nCeOoj9cAIAAAAAC/obi-wan-uncivilized.gif", "AUTHOR says"),
            "subaru scared": ("https://media.tenor.com/bWzTHFTv9bEAAAAC/subaru-natsuke-natsuki-subaru.gif",
                              "AUTHOR is terrified..."),
            "what": ("https://media.tenor.com/rAH8nVxyXxsAAAAC/pet-head.gif", "AUTHOR is very confused..."),
            # AUTHOR interacts with PERSON - interactions with someone else
            "banhammer": ("https://media.tenor.com/MxFIJl3GA6AAAAAC/danganronpa-monokuma.gif", "AUTHOR bans PERSON!"),
            "大丈夫": ("https://media.tenor.com/aUX3FdbuxskAAAAC/emi-emilia.gif",
                       "It\'s okay, PERSON, don\'t worry ❤️"),
            "danganronpa": ("https://media.tenor.com/MxFIJl3GA6AAAAAC/danganronpa-monokuma.gif", "AUTHOR bans PERSON!"),
            "gundyr kick": ("https://media.tenor.com/Vu8um2PYFeUAAAAC/gundyr-kick-gundyr.gif", "AUTHOR kicks PERSON!"),
            "hammer": ("https://media.tenor.com/MxFIJl3GA6AAAAAC/danganronpa-monokuma.gif", "AUTHOR bans PERSON!"),
            "kick": ("https://media.tenor.com/Vu8um2PYFeUAAAAC/gundyr-kick-gundyr.gif", "AUTHOR kicks PERSON!"),
            "punch": ("https://media.tenor.com/fK3dRdJaYv0AAAAC/ora-punch.gif", "AUTHOR punches PERSON rapidly!"),
            "re:zero pat": ("https://media.tenor.com/aUX3FdbuxskAAAAC/emi-emilia.gif", "AUTHOR comforts PERSON"),
            "sorry": ("https://media.tenor.com/iP6_Nm7Mj7UAAAAS/boku-no-hero-academia-gomen.gif",
                      "AUTHOR is really sorry, PERSON"),
            "zhongli bonk": ("https://media.tenor.com/yaEqa7kN91MAAAAd/zhongli-bonk.gif", "AUTHOR bonks PERSON!"),
            # EMPTY - no message in the embed
            "bears dance": ("https://media.tenor.com/G9sLQ4vuEkoAAAAd/dancing-bears.gif", "EMPTY"),
            "echidna spin": ("https://media.tenor.com/Qnad6GUVfRYAAAAC/echidna-rezero.gif", "EMPTY"),
            "glasses": ("https://media.tenor.com/ncWGEFQO73kAAAAC/glasses-anime.gif", "EMPTY"),
            "jetstream sam": ("https://media.tenor.com/GjEULW6A8_wAAAAd/jetstream-sam-my-beloved.gif", "EMPTY"),
            "joker dance": ("https://media.tenor.com/VSOITIeOR4cAAAAd/joker-dance.gif", "EMPTY"),
            "my brain trembles": ("https://media.tenor.com/QxQrHgK5qhwAAAAC/re-zero.gif", "EMPTY"),
            "my source":
                ("https://media.tenor.com/v6Awsd0YO7IAAAAd/metal-gear-rising-metal-gear-rising-revengeance.gif",
                 "EMPTY"),
            "sam": ("https://media.tenor.com/GjEULW6A8_wAAAAd/jetstream-sam-my-beloved.gif", "EMPTY"),
            "sunglasses": ("https://media.tenor.com/u8uX3PwguFwAAAAS/glasses-sunglasses.gif", "EMPTY"),
            "you\'re welcome": ("https://media.tenor.com/LYi_ANHmVxgAAAAd/what-can-i-say-youre-welcome.gif", "EMPTY"),
            # Others
            "bye": ("https://media.tenor.com/VGSF_8J3ujcAAAAC/aurelius467385-re-zero.gif", "Bye!"),
            "emilia": ("https://media.tenor.com/aUX3FdbuxskAAAAC/emi-emilia.gif", "Emilia to make you feel better!"),
            "fight": ("https://media.tenor.com/fK3dRdJaYv0AAAAC/ora-punch.gif", "That\'s what you do with depression"),
            "i have arrived": (
                "https://media.tenor.com/qEs0O052t-0AAAAC/kurumi-tokisaki-kurumi.gif", "Hello everyone!"),
            "no memes in #general": ("https://media.tenor.com/JAGdYpqLEzEAAAAd/batman-discord.gif", "Guys, please...")
        }

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def bearer(self, ctx: commands.context.Context):
        """DS2 players will be confused"""
        text: str
        self.k += 1
        if self.k < 3:
            text = "Bearer...\n" \
                   "Seek...\n" \
                   "Seek...\n" \
                   "Lest..."
        else:
            text = "Bearer of the curse...\n" \
                   "Seek souls. Larger, more powerful souls.\n" \
                   "Seek the King, that is the only way.\n" \
                   "Lest this land swallow you whole... As it has so many others."
            self.k = 0
        await ctx.send(text)

    @commands.command(aliases=["Praise"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def PraiseTheSun(self, ctx: commands.context.Context):
        """
        PRAISE THE SUN!
        """
        for emoji in self.bot.emojis:
            if emoji.name == "Solaire_Praise_The_Sun":
                await ctx.send(str(emoji))
        return

    @commands.hybrid_command()
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def gif(self, ctx: commands.Context, *, args: str):
        """
        Command to send a gif based on the passed arguments
        :param args: name of the gif to send and an optional target of the activity
        """
        # If there is a target to the command, it should be extracted first
        person: str = ""
        if args[-1] == ">":
            i: int = args.index("<")
            person = args[i:]
            some_id: str = person[2:-1]
            member: discord.Member = ctx.guild.get_member(int(some_id))
            if isinstance(ctx.channel, discord.TextChannel) and member.nick is not None:
                person = member.nick
            else:
                person = member.name
            args = args[:i - 1]
        embed: discord.Embed = discord.Embed()
        try:
            url, text = self.gif_dict[args.lower()]
        except KeyError as e:
            print(e.__str__())
            # TODO: Think of a better way to handle no such available gif
            # await ctx.send(f"{args}? Really? No, ask {self.bot.application.owner.name} to make it a feature",
            #                allowed_mentions=discord.AllowedMentions(replied_user=True),
            #                reference=discord.MessageReference.from_message(ctx.message))
            return
        if "PERSON" in text and person == "":
            await ctx.send("You forgot your target", allowed_mentions=discord.AllowedMentions(replied_user=True),
                           reference=discord.MessageReference.from_message(ctx.message))
            return
        embed.set_image(url=url)
        if isinstance(ctx.channel, discord.TextChannel) and ctx.author.nick is not None:
            text = text.replace("AUTHOR", ctx.author.nick)
        else:
            text = text.replace("AUTHOR", ctx.author.name)
        text = text.replace("PERSON", person)
        text = text.replace("EMPTY", "")
        await embed_sending(ctx, embed, text=text)
