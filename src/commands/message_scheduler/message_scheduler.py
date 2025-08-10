import re
from bson import ObjectId
import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from commands.command_bot import CommandBot
from helpers.colours import Colour
from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_scheduler.mongo_utils import *
from helpers.logger import Logger
from helpers.message_utils import *
from helpers.time import *
from helpers.validate import *


class MessageScheduler(
    commands.GroupCog,
    CommandBot,
    group_name="ms",
    group_description="Tools to schedule messages",
):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self._allowed_roles = [
            807340774781878333,
            838169320461697085,
            807340024088625192,
            "👁‍🗨 Head Moderator 👁‍🗨",
            "1145485853641146498",
            "Moderator",
            "Administrator",
        ]

    ####################################################################################
    ################################ AUTOCOMPLETE ######################################
    ####################################################################################
    # add
    async def get_month_choices(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        choices = []

        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }

        for key, value in months.items():
            if current.lower() in f"{key}" or current.lower() in f"{value}":
                choices.append(app_commands.Choice(name=f"{key} | {value}", value=key))

        return choices

    ac_set_day = generate_autocomplete(range(1, 32))
    ac_set_month = generate_autocomplete([], get_month_choices)
    ac_set_year = generate_autocomplete(
        range(datetime.now().year, datetime.now().year + 6)
    )
    ac_set_hour = generate_autocomplete(range(0, 24))
    ac_set_minute = generate_autocomplete(range(0, 60, 5))

    # remove
    async def get_postid_choices(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice]:
        choices = []

        posts = await get_schedule_by_server_id(interaction.guild.id)
        posts = sort_schedules_by_date(posts)

        for post_id, post in posts.items():
            if current.lower() in f"{post_id}":
                choices.append(
                    app_commands.Choice(
                        name=f"{post_id} | {post["message"][:30]}", value=f"{post_id}"
                    )
                )

        return choices

    ac_remove_postid = generate_autocomplete([], get_postid_choices)

    # reaction
    ac_reaction_emojis = generate_autocomplete(["clear"])

    # preview
    ac_preview_target = generate_autocomplete(["current"], get_postid_choices)

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds a set message to the schedule")
    @app_commands.describe(
        channel="The channel to post the scheduled message",
        day="Post day (1-31)",
        month="Post month (1-12)",
        year="Post year",
        hour="Post hour (0-23)",
        minute="Post minute (0-59)",
    )
    @app_commands.autocomplete(
        day=ac_set_day,
        month=ac_set_month,
        year=ac_set_year,
        hour=ac_set_hour,
        minute=ac_set_minute,
    )
    @enrich_command
    async def add(
        self,
        interaction: discord.Interaction,
        channel: str,
        day: app_commands.Range[int, 1, 31],
        month: app_commands.Range[int, 1, 12],
        year: app_commands.Range[int, datetime.now().year],
        hour: app_commands.Range[int, 0, 23],
        minute: app_commands.Range[int, 0, 59],
    ):
        await self.handle_add(
            interaction,
            channel=channel,
            day=day,
            month=month,
            year=year,
            hour=hour,
            minute=minute,
        )

    @app_commands.command(
        name="remove", description="Removes a message from the schedule"
    )
    @app_commands.describe(postid="The scheduled post that you'd like to remove")
    @app_commands.autocomplete(postid=ac_remove_postid)
    @enrich_command
    async def remove(self, interaction: discord.Interaction, postid: str):
        await self.handle_remove(interaction, post_id=postid)

    @app_commands.command(
        name="set", description="Sets a message that'll be added to the schedule later"
    )
    @enrich_command
    async def set(self, interaction: discord.Interaction):
        await self.handle_set(interaction)

    @app_commands.command(
        name="reaction", description="Adds reactions to the current message"
    )
    @app_commands.describe(emojis="A space-separated list of emojis")
    @app_commands.autocomplete(emojis=ac_reaction_emojis)
    @enrich_command
    async def reaction(self, interaction: discord.Interaction, emojis: str):
        await self.handle_set_reaction(interaction, msg=emojis)

    @app_commands.command(name="reset", description="Clears the current message")
    @enrich_command
    async def reset(self, interaction: discord.Interaction):
        await self.handle_reset(interaction)

    @app_commands.command(
        name="clearschedule", description="Removes all scheduled messages"
    )
    @enrich_command
    async def clear_schedule(self, interaction: discord.Interaction):
        await self.handle_clear(interaction)

    @app_commands.command(name="preview", description="Previews a specified message")
    @app_commands.describe(target="Either 'current' or the scheduled post id")
    @app_commands.autocomplete(target=ac_preview_target)
    @enrich_command
    async def preview(self, interaction: discord.Interaction, target: str):
        await self.handle_preview(interaction, target=target)

    @app_commands.command(name="list", description="Lists all scheduled messages")
    @enrich_command
    async def list(self, interaction: discord.Interaction):
        await self.handle_list(interaction)

    @app_commands.command(
        name="help", description="List more info about Message Scheduler commands"
    )
    @enrich_command
    async def help(self, interaction: discord.Interaction):
        await self.handle_help(interaction)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_print(
        self,
        interaction: discord.Interaction,
        channel_id: int | None = None,
        post_id: None | int | ObjectId = None,
    ) -> None:
        # determining which message object to use
        if not post_id:
            message_obj = await get_message_object(interaction.guild.id)
        else:
            schedule = await get_schedule_by_server_id(interaction.guild.id)

            if post_id not in schedule.keys():
                raise ValueError(f"Could not find a post with post ID: {post_id}")

            message_obj = schedule[post_id]

        # adding attachments
        attachments = []

        try:
            if message_obj["attachments"]["message_id"] != "":
                msg = await interaction.channel.fetch_message(
                    int(message_obj["attachments"]["message_id"])
                )

                for f in msg.attachments:
                    file = await f.to_file()
                    attachments.append(file)
        except Exception as e:
            Logger.error(f"Could not add attachments to print: {e}")

        # sending the message
        await send_message(
            interaction=interaction,
            content=message_obj["message"],
            bot=self.bot,
            channel_id=channel_id,
            attachments=attachments,
        )

        msg = [msg async for msg in interaction.channel.history(limit=1)][0]

        try:
            await add_emojis(msg, interaction.guild.emojis, message_obj["reactions"])
        except Exception as e:
            Logger.error(f"Could not add emojis to print: {e}")

    async def handle_add(
        self,
        interaction: discord.Interaction,
        channel: str,
        day: int,
        month: int,
        year: int,
        hour: int,
        minute: int,
    ) -> None:
        date_format = "%d/%m/%YT%H:%M:%S%z"
        date = f"{0 if day < 10 else ""}{day}/{0 if month < 10 else ""}{month}/{"0"*(4-len(f"{year}")) if year < 1000 else ""}{year}"
        time = f"{0 if hour < 10 else ""}{hour}:{0 if minute < 10 else ""}{minute}"

        # argument validation
        validate_channel(channel)
        await validate_date({"date": date, "time": time})

        # formatting the data
        channel = int(channel)
        date_obj = datetime.strptime(date + "T" + time + ":00+00:00", date_format)
        date_obj = convert_to_utc(date_obj, "Canada/Eastern")

        # validating the user's desired time
        await validate_time(date_obj)

        # getting stored message
        msg_obj = await get_message_object(interaction.guild.id)

        # no message was set
        if msg_obj["message"] == "":
            raise ValueError("No message was set! This command was ignored.")

        post_id = ObjectId()

        # db updates
        try:
            schedule_data = {
                "server_id": interaction.guild.id,
                "channel": channel,
                "message": msg_obj["message"],
                "reactions": msg_obj["reactions"],
                "attachments": msg_obj["attachments"],
                "time": date_obj,
            }
        except Exception as e:
            Logger.exception(e)

        try:
            # schedule the current message
            await update_schedule(post_id, schedule_data)
        except Exception as e:
            Logger.exception(e)
            await send_error(interaction, "Could not add the message to the schedule.")
            return

        try:
            # reset the current message
            await update_message_object(
                interaction.guild.id,
                {
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                },
            )
        except Exception as e:
            Logger.exception(e)
            await send_error(
                interaction, "Schedule updated, but the message was not reset."
            )
            return

        # informing the user
        await send_success(
            interaction,
            f"Message added to post schedule!\n\n**Post ID**: {post_id}",
        )

    async def handle_remove(
        self, interaction: discord.Interaction, post_id: str
    ) -> None:
        if not is_valid_id(post_id):
            raise ValueError(f"Invalid post ID: {post_id}.")

        post = await get_post_by_id(parse_id(post_id))

        # no scheduled post corresponds with the provided one
        if not post:
            raise ValueError(
                f"There is no scheduled post with the corresponding post ID: {post_id}"
            )

        # deleting the msg
        try:
            await delete_post_by_id(parse_id(post_id))
        except Exception as e:
            Logger.exception(e)
            await send_error(
                interaction,
                f"Could not delete the post with ID: {post_id}. The command will be ignored.",
            )
            return

        await send_success(
            interaction,
            f"Post with ID {post_id} was removed from the post schedule!",
        )

    async def handle_set(self, interaction: discord.Interaction) -> None:
        # prompting for subsequent input
        msg = await wait_for_msg(interaction, self.bot, title="Set")

        # saving message
        msg_obj = await get_message_object(interaction.guild.id)
        msg_obj["message"] = msg.content
        msg_obj["attachments"] = {
            "message_id": msg.id,
            "channel_id": msg.channel.id,
        }

        await update_message_object(interaction.guild.id, msg_obj)

        # no text was provided
        if msg.content == "":
            await send_success(
                interaction,
                "The message was cleared!",
            )
            return

        await send_success(
            interaction,
            "The message has been set!",
        )

    async def handle_set_reaction(
        self, interaction: discord.Interaction, msg: str
    ) -> None:
        if msg.lower().strip() == "clear":
            msg = ""

        emojis = re.findall("<[a-zA-Z0-9:_]+>|:[a-zA-Z0-9_]+:", msg)

        msg_obj = await get_message_object(interaction.guild.id)

        msg_obj["reactions"] = emojis

        await update_message_object(interaction.guild.id, msg_obj)

        # no emojis specified
        if len(emojis) == 1 and emojis[0] == "":
            await send_success(
                interaction,
                f"Reactions were cleared!",
            )
            return

        await send_success(
            interaction,
            f"Reaction(s) {msg} added to message!",
        )

    async def handle_reset(self, interaction: discord.Interaction) -> None:
        try:
            await update_message_object(
                interaction.guild.id,
                {
                    "message": "",
                    "reactions": [],
                    "attachments": {"message_id": "", "channel_id": ""},
                },
            )
        except Exception as e:
            Logger.exception(e)
            await send_error(
                f"Could not reset the message. The command will be ignored."
            )
            return

        await send_success(
            interaction,
            "The message has been reset!",
        )

    async def handle_clear(self, interaction: discord.Interaction) -> None:
        try:
            await delete_server_posts(interaction.guild.id)
        except Exception as e:
            Logger.exception(e)
            await send_error(
                interaction,
                f"Could not delete all scheduled posts for this server. This command will be ignored.",
            )
            return

        await send_success(
            interaction,
            "The post schedule was cleared!",
        )

    async def handle_preview(
        self, interaction: discord.Interaction, target: str
    ) -> None:
        target = target.lower().strip()

        if target != "current" and not is_valid_id(target):
            raise ValueError("Target must be 'current' or a post ID")

        # determining which message to print
        if target.lower() == "current":
            await self.handle_print(interaction)
        else:
            await self.handle_print(interaction, post_id=parse_id(target))

    async def handle_list(self, interaction: discord.Interaction) -> None:
        schedule = await get_schedule_by_server_id(interaction.guild.id)

        # no scheduled posts
        if not schedule or len(schedule) == 0:
            await send_embedded_message(
                interaction,
                colour=Colour.YELLOW,
                title="Warning",
                desc=f"You don't have any scheduled posts!",
            )
            return

        # returning a list of the schedule
        msg = ""
        msg_list = []

        sorted_items = sort_schedules_by_date(schedule)

        for index, post_id in enumerate(sorted_items):
            msg += (
                f"**#{index + 1}**\n"
                f"**Post ID**: {post_id}\n"
                f"**Post Time**: {schedule[post_id]['time']}\n"
                f"**Preview**: {schedule[post_id]['message'] if len(schedule[post_id]['message']) < 50 else schedule[post_id]['message'][0:47] + '...'}\n\n"
            )

            if len(msg) > 1500:
                msg_list.append(msg)
                msg = ""

        msg_list.append(msg)

        for message in msg_list:
            await send_embedded_message(
                interaction, colour=Colour.GREEN, title="Posts", desc=message
            )

    async def handle_help(self, interaction: discord.Interaction) -> None:
        help_desc = (
            "The Message Scheduler is used to schedule your posts based on the message that you set via the 'set' "
            + f"command (and any modifications made with appropriate commands. E.g. 'reaction'). If you don't like your message, "
            + f"you can override it with another message via the 'set' command, or if you have made other modifications to the "
            + f"message (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.\n\n"
            + f"Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after "
            + f"it has been scheduled, simply use the 'remove' command with the ID that you were provided when the messaged was scheduled.\n\n"
            + f"### The commands are as follows:"
        )

        add_msg = (
            "Adds the created message to the schedule. Note that a message must be created before it can be added to the schedule, "
            + f"times are specified in EST/EDT, and you can only schedule posts for the future (e.g. if the time is 5:04, you can't schedule "
            + f"a post for any time prior to or equal to 5:04).\n\n"
            + f"**Fields**:\n"
            + f"`channel`: channel ID to send post.\n"
            + f"`day`: day of post.\n"
            + f"`month`: month of post.\n"
            + f"`year`: year of post >= current year.\n"
            + f"`hour`: hour of post (0-23).\n"
            + f"`minute`: minute of post (0-59).\n"
            + f">>> Format: `/ms add <channel> <day> <month> <year> <hour> <minute>`\n\n"
            + f"E.g. **/ms add 1143322446909407323 30 1 2023 23 59**\n"
            + f"This would post the message on January 30, 2023 at 11:59 PM to the channel with ID 1143322446909407323"
        )

        remove_msg = (
            "Removes a message from the schedule based on a post ID.\n\n"
            + f"**Fields**:\n"
            + f"`postid`: ID of the post to remove.\n"
            + f">>> Format: `/ms remove <message post id>`\n\n"
            + f"E.g. **/ms remove 123**\n"
            + f"This would remove a post with `id: 123`"
        )

        set_msg = (
            "Sets the message to be scheduled. After submitting this command, the bot will take your next message as the message to be set.\n"
            + f">>> Format: `/ms set`"
        )

        reaction_msg = (
            "Sets the reactions for the message.\n\n"
            + f"**Fields**:\n"
            + f"`emojis`: a list of emojis to add as reactions. `clear` can be input to reset the set reactions.\n\n"
            + f"Note that each emoji is of the format `:<emoji name>:`.\n"
            + f">>> Format: `/ms reaction <emojis>`\n\n"
            + f"E.g. **/ms reaction 😄😢🥯**"
        )

        reset_msg = "Resets the message and all modifications made to it.\n>>> Format: `/ms reset`"

        clear_msg = "Un-schedules all previously scheduled messages\n>>> Format: `/ms clearschedule`"

        preview_msg = (
            "Displays either the message that is currently being worked on (`current`) or a particular scheduled post (`post ID`).\n\n"
            + f"**Fields**:\n"
            + f"`target`: can either be `current` to view the current draft message, or a `post ID` to view a scheduled post.\n"
            + f">>> Format: `/ms preview <target>`\n\n"
            + f"E.g. **/ms preview current**"
        )

        list_msg = (
            "Lists all the currently scheduled messages, with their postID, post time, and a preview of their content. "
            + f"These are ordered by earliest post date first\n>>> Format: `/ms list`"
        )

        fields = [
            {"name": "[1] add", "value": add_msg},
            {"name": "[2] remove", "value": remove_msg},
            {"name": "[3] set", "value": set_msg},
            {"name": "[4] reaction", "value": reaction_msg},
            {"name": "[5] reset", "value": reset_msg},
            {"name": "[6] clearSchedule", "value": clear_msg},
            {"name": "[7] preview", "value": preview_msg},
            {"name": "[8] list", "value": list_msg},
        ]

        await send_embedded_message(
            interaction,
            colour=Colour.PURPLE,
            title="Message Scheduler Commands",
            desc=help_desc,
            fields=fields,
        )


# automatically ran when using load_extensions
async def setup(bot: Bot) -> None:
    # registers cog
    if is_development():
        await bot.add_cog(
            MessageScheduler(bot),
            guild=discord.Object(id=int(os.environ["TEST_DISCORD_SERVER"])),
        )
    else:
        await bot.add_cog(MessageScheduler(bot))
