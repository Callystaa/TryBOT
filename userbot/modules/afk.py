# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import time
from datetime import datetime
from random import choice, randint

from telethon.events import StopPropagation

from userbot.events import register

from userbot import (  # noqa pylint: disable=unused-import isort:skip
    ALIVE_LOGO,
    AFKREASON,
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_MSG,
    ISAFK,
    PM_AUTO_BAN,
    USERS,
)

# ========================= CONSTANTS ============================
AFKSTR = [
    "Aku sibuk. Tolong bicara di dalam tas dan ketika saya kembali Anda bisa memberi saya tas itu!",
    "Saya pergi sekarang. Jika Anda butuh sesuatu, tinggalkan pesan setelah bunyi bep:\n`beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep`!",
    "Anda merindukan saya, lain kali bidik lebih baik.",
    "Saya akan kembali dalam beberapa menit dan jika tidak...,\ntunggu lebih lama.",
    "Saya tidak di sini sekarang, jadi saya mungkin di tempat lain.",
    "Bunga mawar itu berwarna merah,\nBunga violet berwarna biru,\nTinggalkan pesan untukku,\nDan aku akan kembali padamu.",
    "Terkadang hal terbaik dalam hidup pantas untuk ditunggu…\naku akan segera kembali.",
    "I'll be right back,\nbut if I'm not right back,\nI'll be back later.",
    "If you haven't figured it out already,\nI'm not here.",
    "Hello, welcome to my away message, how may I ignore you today?",
    "I'm away over 7 seas and 7 countries,\n7 waters and 7 continents,\n7 mountains and 7 hills,\n7 plains and 7 mounds,\n7 pools and 7 lakes,\n7 springs and 7 meadows,\n7 cities and 7 neighborhoods,\n7 blocks and 7 houses...\n\nWhere not even your messages can reach me!",
    "I'm away from the keyboard at the moment, but if you'll scream loud enough at your screen, I might just hear you.",
    "I went that way\n---->",
    "I went this way\n<----",
    "Please leave a message and make me feel even more important than I already am.",
    "I am not here so stop writing to me,\nor else you will find yourself with a screen full of your own messages.",
    "If I were here,\nI'd tell you where I am.\n\nBut I'm not,\nso ask me when I return...",
    "I am away!\nI don't know when I'll be back!\nHopefully a few minutes from now!",
    "I'm not available right now so please leave your name, number, and address and I will stalk you later.",
    "Sorry, I'm not here right now.\nFeel free to talk to my userbot as long as you like.\nI'll get back to you later.",
    "I bet you were expecting an away message!",
    "Life is so short, there are so many things to do...\nI'm away doing one of them..",
    "I am not here right now...\nbut if I was...\n\nwouldn't that be awesome?",
]
USER_AFK = {}
afk_time = None
afk_start = {}

# =================================================================


@register(outgoing=True, pattern=r"^\.afk(?: |$)(.*)", disable_errors=True)
async def set_afk(afk_e):
    afk_e.text
    string = afk_e.pattern_match.group(1)
    global ISAFK
    global AFKREASON
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    USER_AFK = {}
    afk_time = None
    afk_end = {}
    start_1 = datetime.now()
    afk_start = start_1.replace(microsecond=0)
    if string:
        AFKREASON = string
        await afk_e.edit(
            f"Pergi AFK!\
        \nKarena: `{string}`"
        )
    else:
        await afk_e.edit("Pergi AFK!")
    if BOTLOG:
        await afk_e.client.send_message(BOTLOG_CHATID, "#AFK\nAnda pergi AFK!")
    ISAFK = True
    afk_time = datetime.now()  # pylint:disable=E0602
    raise StopPropagation


@register(outgoing=True)
async def type_afk_is_not_true(notafk):
    global ISAFK
    global COUNT_MSG
    global USERS
    global AFKREASON
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alive = datetime.now()
    afk_end = back_alive.replace(microsecond=0)
    if ISAFK:
        ISAFK = False
        msg = await notafk.respond("Saya tidak lagi AFK.")
        time.sleep(3)
        await msg.delete()
        if BOTLOG:
            await notafk.client.send_message(
                BOTLOG_CHATID,
                "Anda telah menerima "
                + str(COUNT_MSG)
                + " pesan dari "
                + str(len(USERS))
                + " obrolan saat Anda pergi",
            )
            for i in USERS:
                name = await notafk.client.get_entity(i)
                name0 = str(name.first_name)
                await notafk.client.send_message(
                    BOTLOG_CHATID,
                    "["
                    + name0
                    + "](tg://user?id="
                    + str(i)
                    + ")"
                    + " mengirimmu "
                    + "`"
                    + str(USERS[i])
                    + " pesan`",
                )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = None


@register(incoming=True, disable_edited=True)
async def mention_afk(mention):
    global COUNT_MSG
    global USERS
    global ISAFK
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alivee = datetime.now()
    afk_end = back_alivee.replace(microsecond=0)
    afk_since = "a while ago"
    if mention.message.mentioned and not (await mention.get_sender()).bot and ISAFK:
        now = datetime.now()
        datime_since_afk = now - afk_time  # pylint:disable=E0602
        time = float(datime_since_afk.seconds)
        days = time // (24 * 3600)
        time %= 24 * 3600
        hours = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        if days == 1:
            afk_since = "Yesterday"
        elif days > 1:
            if days > 6:
                date = now + datetime.timedelta(
                    days=-days, hours=-hours, minutes=-minutes
                )
                afk_since = date.strftime("%A, %Y %B %m, %H:%I")
            else:
                wday = now + datetime.timedelta(days=-days)
                afk_since = wday.strftime("%A")
        elif hours > 1:
            afk_since = f"`{int(hours)}h{int(minutes)}m` Yang lalu"
        elif minutes > 0:
            afk_since = f"`{int(minutes)}m{int(seconds)}s` Yang lalu"
        else:
            afk_since = f"`{int(seconds)}s` Yang lalu"
        if mention.sender_id not in USERS:
            if AFKREASON:
                await mention.reply(
                    f"Saya AFK sejak {afk_since}.\
                        \nKarena: `{AFKREASON}`"
                )
            else:
                await mention.reply(str(choice(AFKSTR)))
            USERS.update({mention.sender_id: 1})
        else:
            if USERS[mention.sender_id] % randint(2, 4) == 0:
                if AFKREASON:
                    await mention.reply(
                        f"Saya masih AFK sejak {afk_since}.\
                            \nKarena: `{AFKREASON}`"
                    )
                else:
                    await mention.reply(str(choice(AFKSTR)))
            USERS[mention.sender_id] = USERS[mention.sender_id] + 1
        COUNT_MSG = COUNT_MSG + 1


@register(incoming=True, disable_errors=True)
async def afk_on_pm(sender):
    global ISAFK
    global USERS
    global COUNT_MSG
    global COUNT_MSG
    global USERS
    global ISAFK
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alivee = datetime.now()
    afk_end = back_alivee.replace(microsecond=0)
    afk_since = "a while ago"
    if (
        sender.is_private
        and sender.sender_id != 777000
        and not (await sender.get_sender()).bot
    ):
        if PM_AUTO_BAN:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved

                apprv = is_approved(sender.sender_id)
            except AttributeError:
                apprv = True
        else:
            apprv = True
        if apprv and ISAFK:
            now = datetime.now()
            datime_since_afk = now - afk_time  # pylint:disable=E0602
            time = float(datime_since_afk.seconds)
            days = time // (24 * 3600)
            time %= 24 * 3600
            hours = time // 3600
            time %= 3600
            minutes = time // 60
            time %= 60
            seconds = time
            if days == 1:
                afk_since = "Yesterday"
            elif days > 1:
                if days > 6:
                    date = now + datetime.timedelta(
                        days=-days, hours=-hours, minutes=-minutes
                    )
                    afk_since = date.strftime("%A, %Y %B %m, %H:%I")
                else:
                    wday = now + datetime.timedelta(days=-days)
                    afk_since = wday.strftime("%A")
            elif hours > 1:
                afk_since = f"`{int(hours)}h{int(minutes)}m` Yang lalu"
            elif minutes > 0:
                afk_since = f"`{int(minutes)}m{int(seconds)}s` Yang lalu"
            else:
                afk_since = f"`{int(seconds)}s` Yang lalu"
            if sender.sender_id not in USERS:
                if AFKREASON:
                    await sender.reply(
                        f"Saya AFK sejak {afk_since}.\
                        \nKarena: `{AFKREASON}`"
                    )
                else:
                    await sender.reply(str(choice(AFKSTR)))
                USERS.update({sender.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif apprv:
                if USERS[sender.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await sender.reply(
                            f"Saya masih AFK sejak {afk_since}.\
                            \nKarena: `{AFKREASON}`"
                        )
                    else:
                        await sender.reply(str(choice(AFKSTR)))
                USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                COUNT_MSG = COUNT_MSG + 1


CMD_HELP.update(
    {
        "afk": ".afk [Alasan Opsional]\
\nUsage: Menetapkan Anda sebagai afk.\nBalasan untuk siapa saja yang menandai/PM.\
Anda memberi tahu mereka bahwa Anda AFK(karena).\n\nmematikan AFK saat Anda mengetik kembali apa saja, di mana saja.\
"
    }
)
