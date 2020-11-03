# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

import asyncio

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.help(?: |$)(.*)")
async def hep(event):
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
            await asyncio.sleep(15)
            await event.delete()
        else:
            await event.edit("Please specify a valid module name.")
            await asyncio.sleep(5)
            await event.delete()
    else:
        string1 = "Harap tentukan modul mana yang Anda ingin bantuannya !!\nUsage: .help <nama modul>\n\n"
        string = "• "
        string3 = "Daftar untuk semua perintah yang tersedia di bawah ini: "
        string2 = "-------------------------------------------------------------"
        for i in CMD_HELP:
            string += "`" + str(i)
            string += "`  ][  "
        await event.edit(
            f"{string1}" f"{string3}" f"{string2}\n" f"{string}" f"{string2}"
        )
        await asyncio.sleep(120)
        await event.delete()
