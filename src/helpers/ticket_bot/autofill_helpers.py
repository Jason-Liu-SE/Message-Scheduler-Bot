import discord
from discord import app_commands

from helpers.ticket_bot.mongo_utils import *


async def get_reward_choices(
    interaction: discord.Interaction, reward_substr: str
) -> list[app_commands.Choice]:
    choices = []

    reward_substr = reward_substr.strip()

    # rewards that partially match the current input in either id or name
    rewards = await get_many_reward_objects(
        {
            "$or": [
                {"name": {"$regex": reward_substr, "$options": "i"}},
                {
                    "$expr": {
                        "$regexMatch": {
                            "input": {"$toString": "$_id"},
                            "regex": reward_substr,
                            "options": "i",
                        }
                    }
                },
            ]
        },
        sort_field="name",
    )

    for reward_id, reward in rewards.items():
        if (
            reward_substr.lower() in reward["name"].lower()
            or reward_substr.lower() in f"{reward_id}".lower()
        ):
            choices.append(
                app_commands.Choice(
                    name=f"{reward_id} | {reward["name"][:30]}",
                    value=f"{reward_id}",
                )
            )

    return choices
