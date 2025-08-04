from bson import ObjectId
import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot
from discord import app_commands

from functools import cmp_to_key
from helpers.command_helper import *
from helpers.id_helpers import *
from helpers.message_scheduler.mongo_utils import *
from helpers.logger import Logger
from helpers.message_utils import *
from helpers.time import *
from helpers.validate import *


class MessageScheduler(
    commands.GroupCog, group_name="ms", group_description="Tools to schedule messages"
):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.__allowed_roles = [
            807340774781878333,
            838169320461697085,
            807340024088625192,
            "👁‍🗨 Head Moderator 👁‍🗨",
            "1145485853641146498",
            "Moderator",
            "Administrator",
        ]

    ####################################################################################
    ################################### COMMANDS #######################################
    ####################################################################################
    @app_commands.command(name="add", description="Adds a set message to the schedule")
    @app_commands.describe(channel="The channel to post the scheduled message")
    @app_commands.describe(date="The date to post the message")
    @app_commands.describe(time="The time to post the message")
    async def add(
        self, interaction: discord.Interaction, channel: str, date: str, time: str
    ):
        await handle_command(
            self.handle_add, interaction, self.__allowed_roles, channel, date, time
        )

    @app_commands.command(
        name="remove", description="Removes a message from the schedule"
    )
    @app_commands.describe(postid="The scheduled post that you'd like to remove")
    async def remove(self, interaction: discord.Interaction, postid: str):
        await handle_command(
            self.handle_remove, interaction, self.__allowed_roles, postid
        )

    @app_commands.command(
        name="set", description="Sets a message that'll be added to the schedule later"
    )
    @app_commands.describe(msg="Some message to be scheduled")
    async def set(self, interaction: discord.Interaction, msg: str):
        await handle_command(self.handle_set, interaction, self.__allowed_roles, msg)

    @app_commands.command(
        name="reaction", description="Adds reactions to the current message"
    )
    @app_commands.describe(emojis="A space-separated list of emojis")
    async def reaction(self, interaction: discord.Interaction, emojis: str):
        await handle_command(
            self.handle_set_reaction, interaction, self.__allowed_roles, emojis
        )

    @app_commands.command(name="reset", description="Clears the current message")
    async def reset(self, interaction: discord.Interaction):
        await handle_command(self.handle_reset, interaction, self.__allowed_roles)

    @app_commands.command(
        name="clearschedule", description="Removes all scheduled messages"
    )
    async def clear_schedule(self, interaction: discord.Interaction):
        await handle_command(self.handle_clear, interaction, self.__allowed_roles)

    @app_commands.command(name="preview", description="Previews a specified message")
    @app_commands.describe(target="Either 'current' or the scheduled post id")
    async def preview(self, interaction: discord.Interaction, target: str):
        await handle_command(
            self.handle_preview, interaction, self.__allowed_roles, target
        )

    @app_commands.command(name="list", description="Lists all scheduled messages")
    async def list(self, interaction: discord.Interaction):
        await handle_command(self.handle_list, interaction, self.__allowed_roles)

    @app_commands.command(
        name="help", description="List more info about Message Scheduler commands"
    )
    async def help(self, interaction: discord.Interaction):
        await handle_command(self.handle_help, interaction, self.__allowed_roles)

    ####################################################################################
    ################################### HANDLERS #######################################
    ####################################################################################
    async def handle_print(
        self,
        interaction: discord.Interaction,
        channel: int | None = None,
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
                msg = await interaction.channel.fetch_message()(
                    message_obj["attachments"]["message_id"]
                )

                for f in msg.attachments:
                    file = await f.to_file()
                    attachments.append(file)
        except Exception as e:
            Logger.error(e)

        # sending the message
        try:
            msg = await send_message(
                interaction, self.bot, message_obj["message"], channel, attachments
            )
        except RuntimeError as e:
            raise e
        except ValueError as e:
            raise e

        # adding emojis
        for reaction in message_obj["reactions"]:
            try:
                # set to a custom emoji by default
                emoji = discord.utils.get(interaction.guild.emojis, name=reaction)

                if not emoji:  # standard emojis
                    emoji = reaction

                await msg.add_reaction(emoji)
            except:
                Logger.error(f"Unknown emoji: {reaction}")

    async def handle_add(
        self, interaction: discord.Interaction, channel: str, date: str, time: str
    ) -> None:
        date_format = "%d/%m/%YT%H:%M:%S%z"

        # argument validation
        try:
            validate_channel(channel)
            await validate_date({"date": date, "time": time})
        except ValueError as e:
            raise e

        # formatting the data
        channel = int(channel)
        date_obj = datetime.strptime(date + "T" + time + ":00+00:00", date_format)

        # validating the user's desired time
        try:
            await validate_time(date_obj)
        except ValueError as e:
            raise e

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
            Logger.error(e)

        try:
            # schedule the current message
            await update_schedule(post_id, schedule_data)
        except RuntimeError as e:
            Logger.error(e)
            raise RuntimeError("Could not add the message to the schedule.")

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
        except:
            Logger.error(e)
            raise RuntimeError("Schedule updated, but the message was not reset.")

        # informing the user
        await send_embedded_message(
            interaction,
            0x00FF00,
            {
                "title": "Success",
                "desc": f"Message added to post schedule!\n\n**Post ID**: {post_id}",
            },
        )

    async def handle_remove(
        self, interaction: discord.Interaction, post_id: str
    ) -> None:
        if not is_valid_id(post_id):
            raise TypeError(
                f"Invalid post ID: {post_id}. Post IDs may only contain numbers and letters."
            )

        post = await get_post_by_id(parse_id(post_id))

        # no scheduled post corresponds with the provided one
        if not post:
            raise ValueError(
                f"There is no scheduled post with the corresponding post ID: {post_id}"
            )

        # deleting the msg
        try:
            await delete_post_by_id(parse_id(post_id))
        except RuntimeError as e:
            Logger.error(e)
            raise RuntimeError(
                f"Could not delete the post with ID: {post_id}. The command will be ignored."
            )

        await send_embedded_message(
            interaction,
            0x00FF00,
            {
                "title": "Success",
                "desc": f"Post with ID {post_id} was removed from the post schedule!",
            },
        )

    async def handle_set(self, interaction: discord.Interaction, msg: str) -> None:
        msg_obj = await get_message_object(interaction.guild.id)
        msg_obj["message"] = msg
        msg_obj["attachments"] = {
            "message_id": ObjectId(),
            "channel_id": interaction.channel.id,
        }

        await update_message_object(interaction.guild.id, msg_obj)

        # no text was provided
        if msg == "":
            await send_embedded_message(
                interaction,
                0x00FF00,
                {"title": "Success", "desc": "The message was cleared!"},
            )
            return

        await send_embedded_message(
            interaction,
            0x00FF00,
            {"title": "Success", "desc": "The message has been set!"},
        )

    async def handle_set_reaction(
        self, interaction: discord.Interaction, msg: str
    ) -> None:
        emojis = msg.strip().split(" ")

        msg_obj = await get_message_object(interaction.guild.id)

        msg_obj["reactions"] = emojis

        await update_message_object(interaction.guild.id, msg_obj)

        # no emojis specified
        if len(emojis) == 1 and emojis[0] == "":
            await send_embedded_message(
                interaction,
                0x00FF00,
                {"title": "Success", "desc": f"Reactions were cleared!"},
            )
            return

        await send_embedded_message(
            interaction,
            0x00FF00,
            {"title": "Success", "desc": f"Reaction(s) {msg} added to message!"},
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
        except RuntimeError as e:
            Logger.error(e)
            raise RuntimeError(
                f"Could not reset the message. The command will be ignored."
            )

        await send_embedded_message(
            interaction,
            0x00FF00,
            {"title": "Success", "desc": "The message has been reset!"},
        )

    async def handle_clear(self, interaction: discord.Interaction) -> None:
        try:
            await delete_server_posts(interaction.guild.id)
        except RuntimeError as e:
            Logger.error(e)
            raise RuntimeError(
                f"Could not delete all scheduled posts for this server. This command will be ignored."
            )

        await send_embedded_message(
            interaction,
            0x00FF00,
            {"title": "Success", "desc": "The post schedule was cleared!"},
        )

    async def handle_preview(
        self, interaction: discord.Interaction, target: str
    ) -> None:
        target = target.lower()

        if target != "current" and not is_valid_id(target):
            raise ValueError("Target must be 'current' or a post ID")

        # determining which message to print
        try:
            if target.lower() == "current":
                await self.handle_print(interaction)
            else:
                await self.handle_print(interaction, post_id=parse_id(target))
        except RuntimeError as e:
            raise e
        except ValueError as e:
            raise e

    async def handle_list(self, interaction: discord.Interaction) -> None:
        schedule = await get_schedule_by_server_id(interaction.guild.id)

        # no scheduled posts
        if not schedule or len(schedule) == 0:
            await send_embedded_message(
                interaction,
                0xFFFF00,
                {"title": "Warning", "desc": f"You don't have any scheduled posts!"},
            )
            return

        # returning a list of the schedule
        msg = ""
        msg_list = []

        sorted_items = dict(
            sorted(
                schedule.items(),
                key=cmp_to_key(lambda a, b: 1 if a[1]["time"] > b[1]["time"] else -1),
            )
        )

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
                interaction, 0x00FF00, {"title": "Posts", "desc": message}
            )

    async def handle_help(self, interaction: discord.Interaction) -> None:
        help_desc = """The Message Scheduler is used to schedule your posts based on the message that you set via the 'set' command (and any modifications made with appropriate commands. E.g. 'reaction'). If you don't like your message, you can override it with another message via the 'set' command, or if you have made other modifications to the message (e.g. via 'reaction'), you can use the 'reset' command to reset the message entirely.
    Once you are happy with the message, you can schedule it via the 'add' command. If you want to delete the message after it has been scheduled, simply use the 'remove' command with the ID that you were provided when the messaged was scheduled.
        
    The commands are as follows:"""

        add_msg = """Adds the created message to the schedule. Note that a message must be created before it can be added to the schedule, times are specified in UTC, and you can only schedule posts for the future (e.g. if the time is 5:04, you can't schedule a post for any time prior to or equal to 5:04).
        
    BTW:
    UTC Time = EDT Time + 4 hours
    UTC Time = EST Time + 5 hours
        
    Format: !ms add <channel> <post date> <post time>
        
    E.g. !ms add 1143322446909407323 30/01/2023 23:59
    This would post the message on January 30, 2023 at 11:59 PM to the channel with ID 1143322446909407323"""

        remove_msg = """Removes a message from the schedule based on a post ID.
        
    Format: !ms remove <message post id>
        
    E.g. !ms remove 123"""

        set_msg = """Sets the message to be scheduled.
        
    Format: !ms set <message>
        
    E.g. !ms set This is an announcement"""

        reaction_msg = """Sets the reactions for the message.
        
    Format: !ms reaction [<emoji>]
        
    E.g. !ms reaction 😄 😢 🥯"""

        reset_msg = """Resets the message and all modifications made to it
        
    Format: !ms reset
        
    E.g. !ms reset"""

        clear_msg = """Un-schedules all previously scheduled messages
        
    Format: !ms clearSchedule
        
    E.g. !ms clearSchedule"""

        preview_msg = """Displays either the message that is currently being worked on or a particular scheduled post.
        
    Format: !ms preview <current|post ID>
        
    E.g. !ms preview current"""

        list_msg = """Lists all the currently scheduled messages, with their postID, post time, and a preview of their content.
        
    Format: !ms list
        
    E.g. !ms list"""

        fields = [
            {"name": "add", "value": add_msg},
            {"name": "remove", "value": remove_msg},
            {"name": "set", "value": set_msg},
            {"name": "reaction", "value": reaction_msg},
            {"name": "reset", "value": reset_msg},
            {"name": "clearSchedule", "value": clear_msg},
            {"name": "preview", "value": preview_msg},
            {"name": "list", "value": list_msg},
        ]

        await send_embedded_message(
            interaction,
            0x7E42F5,
            {"title": "Message Scheduler Commands", "desc": help_desc},
            fields,
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
