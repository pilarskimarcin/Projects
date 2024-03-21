from dotenv import load_dotenv
from os import getenv
import subprocess
from typing import List

import discord
from discord.ext import commands
import logging

# from keep_alive import keep_alive
# Cogs
from cogs.cog_moderation import Moderation
from cogs.cog_logging import Logging, save_emergency_log
from cogs.cog_self_checking import SelfCheck
from cogs.cog_fun import Fun

load_dotenv()

# Logging everything in a file
logger: logging.Logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler: logging.FileHandler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Enabling proper intents, so it's possible to get the members' list
intents: discord.flags.Intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class WraithBot(commands.Bot):
    maintenance: bool

    async def load_cogs(self) -> bool:
        # Adding cogs
        cogs_loaded: bool = False
        await self.add_cog(Moderation(self))
        await self.add_cog(Logging(self))
        await self.add_cog(SelfCheck(self))
        await self.add_cog(Fun(self))
        if set(self.cogs.keys()) == {'Moderation', 'Logging', 'SelfCheck', 'Fun'}:
            cogs_loaded = True
        return cogs_loaded

    async def setup_hook(self):
        self.maintenance = False  # Needed to decide whether to start the timed message
        cogs_loaded: bool = await self.load_cogs()
        if not cogs_loaded:
            print("Error loading cogs")
        else:
            print("Cogs loaded")
        synced: List[discord.app_commands.AppCommand] = await self.tree.sync()
        print(f"Synced AppCommands: {synced}")
        # Maintencance mode - to run locally without important commands
        if self.maintenance:
            self.remove_listener(Moderation.add_to_muted_channel)
            self.remove_listener(Moderation.remove_from_muted_channel)
            self.remove_listener(Moderation.platforms)


# the Client - the user "account" representing the bot
client: WraithBot = WraithBot(command_prefix=["Wraith ", "wraith ", "WRAITH ", "WrAiTh "],
                              case_insensitive=True,
                              activity=discord.Activity(type=discord.ActivityType.watching, name='the chat'),
                              intents=intents,
                              help_command=None)

if __name__ == '__main__':
    try:
        # keep_alive()
        client.run(getenv('TOKEN'), log_handler=handler)
    # If the shared IP of replit is rate-limited
    except discord.errors.HTTPException as error:
        if error.status == 429:
            print("HTTPException detected!")
            save_emergency_log()
            print("Log saved!")
            client.get_cog("SelfCheck").rate_limit_flag = True
            subprocess.run(["kill", "1"], shell=True, capture_output=True)
