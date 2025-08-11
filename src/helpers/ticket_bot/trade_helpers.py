import discord

from helpers.colours import Colour
from helpers.message_utils import generate_embedded_message
from helpers.ticket_bot.mongo_utils import *


def update_confirmation_state(
    responding_user_id: int, confirmation_states: dict[int, bool], new_state: bool
) -> None:
    for key, _ in confirmation_states.items():
        if responding_user_id == key:
            confirmation_states[key] = new_state
            break
    return confirmation_states


async def update_trade_msg(
    view: discord.ui.View,
    msg_embed_ref: discord.Embed,
    desc: str,
    is_successful: bool | None = None,
) -> None:
    msg_title = msg_embed_ref.title
    msg_colour = msg_embed_ref.colour
    msg_view = view

    if is_successful != None:
        msg_view = None

        if is_successful:
            msg_title = f"{msg_embed_ref.title}: Complete  :white_check_mark:"
            msg_colour = Colour.GREEN
        else:
            msg_title = f"{msg_embed_ref.title}: Cancelled  :x:"
            msg_colour = Colour.RED

    update_embed = generate_embedded_message(
        title=msg_title,
        desc=desc,
        colour=msg_colour,
    )

    if (
        not hasattr(view, "msg_ref")
        or not view.msg_ref
        or not hasattr(view.msg_ref, "edit")
    ):
        raise Exception("Could not update trade message")

    await view.msg_ref.edit(embed=update_embed, view=msg_view)


def display_confirmation(has_confirmed: bool):
    return ":white_check_mark:" if has_confirmed else ":x:"


async def complete_trade(
    instigator_user: discord.Member,
    target_user: discord.Member,
    user_objs: dict,
    tickets: int,
    send_direction: Literal[
        "instigator_to_target", "target_to_instigator"
    ] = "instigator_to_target",
) -> None:
    invert = 1 if send_direction == "instigator_to_target" else -1

    user_objs[instigator_user.id]["tickets"] -= tickets * invert
    user_objs[target_user.id]["tickets"] += tickets * invert

    await update_user_objects(user_objs)


async def verify_trade_users(
    instigator_user: discord.Member,
    target_user: discord.Member,
    tickets: int,
    check_instigator_balance: bool = True,
    check_target_balance: bool = True,
) -> dict:
    user_objs = await get_user_objects([instigator_user.id, target_user.id])

    target_exists = target_user.id in user_objs
    instigator_exists = instigator_user.id in user_objs

    if not target_exists and not instigator_exists:
        raise ValueError(
            f"{instigator_user.mention} and {target_user.mention} do not exist in the system. Please contact an administrator or moderator."
        )
    elif not target_exists or not instigator_exists:
        raise ValueError(
            f"{target_user.mention if not target_exists else instigator_user.mention} does not exist in the system. Please contact an administrator or moderator."
        )

    instigator_lacks_tickets = user_objs[instigator_user.id]["tickets"] < tickets
    target_lacks_tickets = user_objs[target_user.id]["tickets"] < tickets

    if (
        check_instigator_balance
        and check_target_balance
        and instigator_lacks_tickets
        and target_lacks_tickets
    ):
        raise ValueError(
            f"{instigator_user.mention} and {target_user.mention} do not have enough tickets for this trade."
        )
    elif (check_instigator_balance and instigator_lacks_tickets) or (
        check_target_balance and target_lacks_tickets
    ):
        raise ValueError(
            f"{target_user.mention if check_target_balance and target_lacks_tickets else instigator_user.mention} does not have enough tickets for this trade."
        )

    return user_objs
