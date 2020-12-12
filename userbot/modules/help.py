# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""Userbot help command"""

import asyncio

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.help(?: |$)(.*)")
async def help(event):
    """For .help command"""
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            msg = await event.edit(str(CMD_HELP[args]))
        else:
            msg = await event.edit("Masukin module yang bener ngab.")
    else:
        string = "Tentukan modul mana yang Anda ingin bantuannya !!\n**Usage:** `.help` <nama modul>\n\n"
        for i in sorted(CMD_HELP):
            string += "`" + str(i) + "`"
            string += "\t\t\t||\t\t\t "
        msg = await event.edit(string)
    await asyncio.sleep(60)
    try:
        await msg.delete()
    except BaseException:
        return  # just in case if msg deleted first
