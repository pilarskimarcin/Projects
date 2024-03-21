from csv import reader, writer
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, List, Dict, Set

import discord
from discord.ext import commands, tasks

# Setup
servers_dict: Dict[str, int] = {
    "DS_SERVER": 729353421483933716,  # Dark Souls Community
    "MY_SERVER": 690212035757211663  # ShadowHunter's server
}


# A class to represent all important roles from the server
class Roles:
    mandatory: List[int]
    exclusions: List[int]
    groups_list: List[List[int]]
    groups_dict: Dict[str, List[int]]

    def __init__(self, mandatory: List[int], exclusions: List[int], groups: Dict[str, List[int]]):
        self.mandatory = mandatory
        self.exclusions = exclusions
        self.groups_list = list(groups.values())
        self.groups_dict = groups

    def __str__(self):
        return "Mandatory roles:\n" + ", ".join([str(el) for el in self.mandatory]) + \
            "\nExclusions:\n" + ", ".join([str(el) for el in self.exclusions]) + \
            "\nGROUPS:\n" + "\n".join([
                f"{key}: " + ", ".join([
                    str(el) for el in self.groups_dict[key]
                ]) for key in self.groups_dict.keys()
            ])


def get_roles_from_file(server: discord.Guild, only_mandatory: bool = False, only_groups: bool = False) -> Roles:
    # Choosing the appropriate files with server's roles
    server_file: str = "servers/"
    server_file += server.name

    mandatory_ids: List[int]
    exclusions_ids: List[int]
    if only_groups:
        mandatory_ids = []
        exclusions_ids = []
    else:
        # Obtaining mandatory roles and exclusions
        with open(server_file + "/mandatory and exclusions.txt") as f:
            lines: List[str] = f.readlines()
            i: int = lines.index("Mandatory:\n")
            j: int = lines.index("Exclusions:\n")
            mandatory_ids: List[int] = [int(el) for el in "".join(lines[i + 1:j - 1]).split()]
            exclusions_ids: List[int] = [int(el) for el in "".join(lines[j + 1:]).split()]
            f.close()

    groups_of_ids: Dict[str, List[int]] = {}
    if only_mandatory:
        pass
    else:
        # Obtaining groups of roles
        with open(server_file + "/groups.csv") as f:
            csvreader = reader(f)
            for row in csvreader:
                groups_of_ids[row[0]] = [int(el) for el in row[1:]]
    return Roles(mandatory_ids, exclusions_ids, groups_of_ids)


def add_mandatory_or_exclusion(ctx: commands.Context, roles_to_add: List[str], mandatory: bool):
    server: discord.Guild = ctx.guild
    old_roles: Roles = get_roles_from_file(server, only_mandatory=True)
    names: Set[str] = set(roles_to_add)
    ids: Set[int] = set()
    for role in server.roles:
        if role.name in names:
            ids.add(role.id)
    new_mandatory: Set[int] = set(old_roles.mandatory)
    new_exclusions: Set[int] = set(old_roles.exclusions)
    if mandatory:
        new_mandatory = new_mandatory.union(ids)
    else:
        new_exclusions = new_exclusions.union(ids)
    with open(f"servers/{server.name}/mandatory and exclusions.txt", "w") as f:
        new_lines: List[str] = ["Mandatory:\n"]
        new_lines.extend([str(role_id) + "\n" for role_id in new_mandatory])
        new_lines.extend(["\n", "Exclusions:\n"])
        new_lines.extend([str(role_id) + "\n" for role_id in new_exclusions])
        # new_lines.extend(["\n"])
        f.truncate()
        f.seek(0)
        f.writelines(new_lines)
        f.close()


# How long someone has been on the server, returned as a number of seconds or as a timedelta object
def user_time_on_the_server(user: discord.Member, timestamp=False) -> Union[float, timedelta]:
    if timestamp:
        return abs(
            datetime.now(timezone.utc).timestamp() - user.joined_at.replace(tzinfo=timezone.utc).timestamp()
        )
    else:
        return abs(datetime.now(timezone.utc) - user.joined_at)


def check_if_ds_server(ctx: commands.Context):
    return ctx.guild is not None and ctx.guild.id == servers_dict["DS_SERVER"]


class Moderation(commands.Cog):
    bot: commands.Bot
    found_guilty: str

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.found_guilty = ""
        # Commented out - no longer needed
        # if not self.bot.maintenance:
        #     self.elden_ring.start()

    @tasks.loop(hours=6.0)
    async def elden_ring(self) -> None:
        """
        A predefined message sent every X hours (depending on the parameter in the tasks.loop()
        """
        server: discord.Guild = await self.bot.fetch_guild(servers_dict["DS_SERVER"])
        channel: discord.TextChannel = await server.fetch_channel(944518068518912000)
        await channel.send("**CENSOR ALL BOSS, NPC, AND LOCATION (if it contains a boss' name) NAMES WITH "
                           "|| ON EACH SIDE OF YOUR TEXT**\n\|\|censored\|\| -> ||censored||\n"
                           "*Check pins for more details/examples. Not following this rule will "
                           "result in a warn.*")
        print(str(datetime.now()) + " - sent the message")

    @elden_ring.before_loop
    async def before_printer(self) -> None:
        await self.bot.wait_until_ready()

    def cog_unload(self) -> None:
        self.elden_ring.cancel()

    def cog_check(self, ctx: commands.context.Context):
        # Only staff is allowed to use commands from this cog
        if ctx.guild is not None:
            if ctx.guild.id == servers_dict["DS_SERVER"]:
                mod_roles: List[int] = [
                    739204725354004566, 729358669975912448, 738271984378445824
                ]  # Gods, Royalty, Four Knights of Gwyn
                return len(set([role.id for role in ctx.author.roles]).intersection(set(mod_roles))) > 0
            elif ctx.guild.id == servers_dict["MY_SERVER"]:
                return True
        else:
            return False

    @commands.command()
    async def when(self, ctx: commands.context.Context, user_id: int):
        """
        Shows how long someone has been in the server
        """
        member: discord.Member = ctx.guild.get_member(user_id)
        delta: timedelta = user_time_on_the_server(member)
        hours: int = delta.seconds // 3600
        msg: str = f"User {member.__str__()} has last joined the server " \
                   f"{delta.days} days, {hours} hours and {delta.seconds // 60 - 60 * hours} minutes ago"
        await ctx.send(msg)

    @commands.is_owner()
    @commands.command()
    async def server_info(self, ctx: commands.context.Context, *, server_name: str):
        """
        Basic information about the server
        """
        for guild in self.bot.guilds:
            if guild.name == server_name:
                await ctx.send(f"Server name: {guild.name}, id: {guild.id}, owner: {guild.owner.__str__()}")
                return
        await ctx.send("First bring me with you to that server")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def seek(self, ctx: commands.context.Context, *, optional_args: Optional[str] = None):
        """
        Seeking out members without roles, according to what was saved about the server
        :param optional_args: possible to add "-all" or "-roles" to bypass the time limit or to display also the roles
            of the found users
        """
        # Whether to only take into account users who have already been in the server for 2 hours
        time_limit: bool = True
        # Whether to also send the users' roles, not just their names and IDs
        add_roles: bool = False
        # Checking if there are any optional arguments
        if optional_args:
            args: List[str] = optional_args.split()
            if "-all" in args:
                time_limit = False
            if "-roles" in args:
                add_roles = True
        server: discord.Guild = ctx.guild
        try:
            server_roles: Roles = get_roles_from_file(server)
        except ValueError:
            await ctx.send("Uhm... I don't know roles for this server?")
            app_info: discord.AppInfo = await self.bot.application_info()
            await app_info.owner.send(f"Do we have all servers' roles set up?\nContext: {ctx.message.jump_url}")
            return

        # The "seeking"
        found: str = ""

        def finding_the_guilty():
            nonlocal found
            if f"{str(member)}, {member.id}" in found:
                return
            found += f"{str(member)}, {member.id}"
            if add_roles:
                found += f" - roles: {','.join([role.name for role in member.roles])}"
            found += "\n"
            return

        for member in server.members:
            delta: float = user_time_on_the_server(member, timestamp=True)
            # Omit users who have joined less than 2 hours ago
            if time_limit and abs(delta) < 7200:
                continue
            # User's roles, by ID
            roles: Set[int] = set([role.id for role in member.roles])
            # Omit users with roles saved as being exclusions
            if len(set(server_roles.exclusions).intersection(roles)) > 0:
                continue
            # Checking if a member has all the obligatory roles -> by using the sets' subset
            if not set(server_roles.mandatory).issubset(roles):
                finding_the_guilty()
            # Checking if a member has at least one role from each group
            for group in server_roles.groups_list:
                if len(set(group).intersection(roles)) == 0:
                    finding_the_guilty()
        if len(found) == 0:
            await ctx.send("No more victims...")
        else:
            await ctx.send(found)
            self.found_guilty = found

            # Retain the found users for 30 seconds, then clear it from memory
            await discord.utils.sleep_until(datetime.now() + timedelta(seconds=30))
            self.found_guilty = ""

    @commands.command()
    async def generate_kicks(self, ctx: commands.Context):
        """
        Generating a list of kicks of the users found in seek
        """
        if self.found_guilty == "":
            await ctx.send("I haven't yet found anyone (or already forgot them)\nUse `seek -roles` first")
            return
        for line in self.found_guilty.split("\n"):
            if not line:
                continue
            line_parts = line.split()
            user_id: str = ""
            for part in line_parts:
                if part.isnumeric():
                    user_id = part
                    break
            if line_parts[-1] == "@everyone":
                await ctx.send("%kick " + user_id + " to get access to the server, read the rules first")
            else:
                await ctx.send("%kick " + user_id + " not getting roles")

    @commands.command()
    async def roles(self, ctx: commands.Context):
        """
        Showing saved roles
        """
        roles: Roles = get_roles_from_file(ctx.guild)
        mandatory_names: List[str] = []
        exclusions_names: List[str] = []

        def finding_role_names(role_id: int, roles_list: List[str]):
            for role in ctx.guild.roles:
                if role.id == role_id:
                    roles_list.append(role.name)
                    break

        for m_role in roles.mandatory:
            finding_role_names(m_role, mandatory_names)
        for e_role in roles.exclusions:
            finding_role_names(e_role, exclusions_names)
        groups: Dict[str, List[str]] = {}
        for key, value in roles.groups_dict.items():
            group: List[str] = []
            for g_role in value:
                finding_role_names(g_role, group)
            groups[key] = group
        message: str = "Mandatory roles:\n" + ", ".join(mandatory_names) + \
                       "\nExclusions:\n" + ", ".join(exclusions_names) + \
                       "\nGROUPS:\n" + "\n".join([f"{key}: " + ", ".join(groups[key]) for key in groups.keys()])
        await ctx.send(message)

    @commands.group(case_insensitive=True)
    async def add(self, ctx: commands.Context):
        """
        A command group allowing to add more roles to those tracked by the bot
        """
        # When invoked with not enough arguments
        if ctx.invoked_subcommand is None:
            await ctx.send("Not enough arguments. For details, use `Wraith add help`")

    @add.command()
    async def help(self, ctx: commands.Context):
        nbsp: str = "\xa0"
        help_msg: str = "IMPORTANT NOTES: `<role>` means the\n" \
                        f"{10 * nbsp}precise __name__ of the role; divide roles\n" \
                        f"{10 * nbsp}with \"`, `\"\n" \
                        "\n" \
                        "`Wraith add mandatory <role1>, <role2>` -\n" \
                        f"{10 * nbsp}adds roles 1, 2, ... to the list of roles, that\n" \
                        f"{10 * nbsp}everyone must have (every single one of\n" \
                        f"{10 * nbsp}them)\n" \
                        "`Wraith add exclusion <role1>, <role2>` -\n" \
                        f"{10 * nbsp}adds roles 1, 2, ... to the list of roles, that\n" \
                        f"{10 * nbsp}should be excluded from seeking, for\n" \
                        f"{10 * nbsp}example a role for bots, so they aren't found \n" \
                        f"{10 * nbsp}even if they don't have enough roles\n" \
                        "`Wraith add group <group name> <role1>,`\n" \
                        f"{10 * nbsp}`<role2>` - adds a group of roles so that\n" \
                        f"{10 * nbsp}everyone must have at least __one role from__ \n" \
                        f"{10 * nbsp}__the group__, for example platform roles,\n" \
                        f"{10 * nbsp}someone can have a PC role, someone else\n" \
                        f"{10 * nbsp} a PS4 role, both of them satisfy the role\n" \
                        f"{10 * nbsp}requirements"
        embed: discord.Embed = discord.Embed(description=help_msg)
        embed.set_author(name="Adding more roles", icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @add.command()
    async def mandatory(self, ctx: commands.Context, *, roles_to_add: str):
        """
        Adding mandatory roles to the server's roles
        :param roles_to_add: a list of the names of roles to add
        """
        roles_list: List[str] = roles_to_add.split(", ")
        if len(roles_list) == 0:
            await ctx.send("No roles have been added")
            return
        add_mandatory_or_exclusion(ctx, roles_list, mandatory=True)
        await ctx.send(f"Roles {roles_to_add} added successfully")
        app_info: discord.AppInfo = await self.bot.application_info()
        await app_info.owner.send(f"Mandatory roles {roles_to_add} have been added on {ctx.guild}")

    @add.command()
    async def exclusion(self, ctx: commands.Context, *, roles_to_add: str):
        """
        Adding exclusion roles to the server's roles
        :param roles_to_add: a list of the names of roles to add
        """
        roles_list: List[str] = roles_to_add.split(", ")
        if len(roles_list) == 0:
            await ctx.send("No roles have been added")
            return
        add_mandatory_or_exclusion(ctx, roles_list, mandatory=False)
        await ctx.send(f"Roles {roles_to_add} excluded successfully")
        app_info: discord.AppInfo = await self.bot.application_info()
        await app_info.owner.send(f"Exclusion roles {roles_to_add} have been added on {ctx.guild}")

    @add.command()
    async def group(self, ctx: commands.Context, group_name: str, *, roles_to_add: str):
        """
        Adding a whole group of roles to the server's roles
        :param group_name: the name of the group
        :param roles_to_add: a list of the names of roles to add
        """
        roles_list: List[str] = roles_to_add.split(", ")
        if len(roles_list) == 0:
            await ctx.send("No roles have been added")
            return
        server: discord.Guild = ctx.guild
        old_roles: Roles = get_roles_from_file(server, only_groups=True)
        names: Set[str] = set(roles_list)
        ids: Set[int] = set()
        for role in server.roles:
            if role.name in names:
                ids.add(role.id)
        groups_values = old_roles.groups_dict.values()
        old_ids: List[int] = []
        for group in groups_values:
            old_ids.extend(group)
        if len(set(old_ids).intersection(ids)) > 0 or group_name in old_roles.groups_dict.keys():
            await ctx.send("At least some of these roles have already been added")
        else:
            new_dict: Dict[str, List[int]] = old_roles.groups_dict
            new_dict[group_name] = list(ids)
            with open(f"servers/{server.name}/groups.csv", "w", newline="") as f:
                csvwriter = writer(f)
                for key, value in new_dict.items():
                    csvwriter.writerow([key] + [str(el) for el in value])
                f.close()
            await ctx.send(f"Group {group_name} added successfully")
            app_info: discord.AppInfo = await self.bot.application_info()
            await app_info.owner.send(
                f"Group {group_name} with roles: {roles_to_add} has been added on {ctx.guild}"
            )

    # DO NOT UNCOMMENT
    # Remember your failure
    # @commands.command()
    # async def inactive(self, ctx: commands.context.Context, days_inactive: int):
    #     server: discord.Guild = ctx.guild
    #     return
    #     await server.prune_members(days=days_inactive, roles=server.roles)
    # DO NOT UNCOMMENT

    @commands.check(check_if_ds_server)
    @commands.command()
    async def colour_fix(self, ctx: commands.Context):
        """
        Command to help adding the No_colour role to those without it and removing it from those who got a colour role
        """
        no_colour_role: discord.Role = ctx.guild.get_role(808588081216487484)  # No colour role
        with open("servers/Dark Souls Community/colour_roles.txt") as f:
            names: Set[str] = set(f.read().split("\n"))
            f.close()
        members_no_colour: str = "Throw the poop!"
        members_colour: str = "Clean these ones:"
        for member in ctx.guild.members:
            delta: float = user_time_on_the_server(member, timestamp=True)
            # Omit users who have joined less than 2 hours ago
            if abs(delta) < 7200:
                continue
            member_roles: Set[str] = set([role.name for role in member.roles])
            if len(member_roles.intersection(names)) == 0:
                if no_colour_role.name not in member_roles:
                    members_no_colour += f"\n{str(member)}, {member.id}"
            else:
                if no_colour_role.name in member_roles:
                    members_colour += f"\n{str(member)}, {member.id}"
        if members_no_colour == "Throw the poop!":
            members_no_colour = "Everyone is colourful!"
        if members_colour == "Clean these ones:":
            members_colour = "The only unclean are those who are rightly so..."
        await ctx.send(members_no_colour + "\n" + members_colour)

    @commands.check(check_if_ds_server)
    @commands.Cog.listener("on_message")
    async def platforms(self, message: discord.Message):
        """
        A listener adding emojis of the user's platform roles under their message, if they contain the "help" keyword
        """
        if message.channel.id not in [
            729357183963103274, 729357281241858108, 729357323771969626, 729357357049708675, 729357389308100679,
            729357421142867998, 944518068518912000
        ]:  # [960429666051711016, 789573175016816710]:
            return
        if "help" in message.content.lower():
            platform_roles: Set[int] = set(get_roles_from_file(message.guild).groups_dict["Platform"])
            emoji_dict: Dict[str, str] = {
                "PC": "\U0001F5A5",
                "PS3": "PS3",
                "PS4": "PS4",
                "PS5": "PS5",
                "XBOX 360": "XBOX360",
                "XBOX 1": "XboxOne",
                "Xbox Series X": "XBoxSeriesX",
                "SWITCH": "Switch"
            }
            user: discord.Member = message.author
            for role in set([role.id for role in user.roles]).intersection(platform_roles):
                emoji_name: str = emoji_dict[user.get_role(role).name]
                emoji: Union[discord.Emoji, str] = discord.utils.get(self.bot.emojis, name=emoji_name)
                if not emoji:
                    emoji = emoji_name
                try:
                    await message.add_reaction(emoji)
                except Exception as e:
                    print(e)
                    await self.bot.application.owner.send(f"Error in reaction adding - {message.channel.name} in "
                                                          f"{message.guild}, link: {message.jump_url}")
            # Soul memory for the DS2
            if message.channel.id == 729357357049708675:
                emoji: Union[discord.Emoji, str] = discord.utils.get(self.bot.emojis, name="SoulMemoryByYURI")
                try:
                    await message.add_reaction(emoji)
                except Exception as e:
                    print(e)
                    await self.bot.application.owner.send(f"Error in reaction adding - {message.channel.name} in "
                                                          f"{message.guild}, link: {message.jump_url}")

    @commands.check(check_if_ds_server)
    @commands.Cog.listener("on_member_update")
    async def add_to_muted_channel(self, before: discord.Member, after: discord.Member):
        """
        Adding a user to the muted channel of the DS Community server to fix Dyno's mistakes
        """
        muted_role: int = 733511228902735942
        muted_channel_id: int = 876219354323251210
        before_roles: List[int] = [role.id for role in before.roles]
        after_roles: List[int] = [role.id for role in after.roles]
        if muted_role in after_roles and muted_role not in before_roles:
            muted_channel: discord.abc.GuildChannel = before.guild.get_channel(muted_channel_id)
            await muted_channel.set_permissions(after, read_messages=True, send_messages=True, add_reactions=True)

    @commands.check(check_if_ds_server)
    @commands.Cog.listener("on_member_update")
    async def remove_from_muted_channel(self, before: discord.Member, after: discord.Member):
        """
        Reversing changes to the muted channel - see add_to_muted_channel
        """
        muted_role: int = 733511228902735942
        muted_channel_id: int = 876219354323251210
        before_roles: List[int] = [role.id for role in before.roles]
        after_roles: List[int] = [role.id for role in after.roles]
        if muted_role in before_roles and muted_role not in after_roles:
            muted_channel: discord.abc.GuildChannel = before.guild.get_channel(muted_channel_id)
            await muted_channel.set_permissions(after, overwrite=None)
