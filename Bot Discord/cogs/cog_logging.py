from typing import List

from discord.ext import commands


# Logs
def _save_log(filename_to_save: str):
    with open("discord.log", 'r') as f:
        with open(filename_to_save, "w") as f_new:
            lines: List[str] = f.readlines()
            f_new.writelines(lines)
            f_new.close()
        f.close()


def save_emergency_log():
    _save_log("Emergency_exit.log")


class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def save_log(self, ctx: commands.context.Context):
        _save_log("saved_log.txt")
        await ctx.send("Log saved")
