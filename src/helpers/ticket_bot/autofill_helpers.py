import discord
from discord import app_commands

from helpers.ticket_bot.mongo_utils import *


async def get_reward_choices(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice]:
    choices = []

    current = current.strip()

    # rewards that partially match the current input in either id or name
    rewards = await get_many_reward_objects(
        {
            "$or": [
                {"name": {"$regex": current, "$options": "i"}},
                {
                    "$expr": {
                        "$regexMatch": {
                            "input": {"$toString": "$_id"},
                            "regex": current,
                            "options": "i",
                        }
                    }
                },
            ]
        },
        sort_field="name",
    )

    for reward_id, reward in rewards.items():
        if current.lower() in reward["name"] or current.lower() in f"{reward_id}":
            choices.append(
                app_commands.Choice(
                    name=f"{reward_id} | {reward["name"][:30]}",
                    value=f"{reward_id}",
                )
            )

    return choices
