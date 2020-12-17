# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to the \
    Information Superhighway (yes, Internet). """

from datetime import datetime

from speedtest import Speedtest
from telethon import functions

from userbot import CMD_HELP
from userbot.events import register


async def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


@register(outgoing=True, pattern=r"^\.speed$")
async def speedtst(spd):
    await spd.edit("`Tes kecepatan . . .`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    output = f"Dimulai pada `{result['timestamp']}`\n\n"
    output += "`Client:`\n"
    output += f"ISP: `{result['client']['isp']}`\n"
    output += f"Negara: `{result['client']['country']}`\n\n"
    output += "`Server:`\n"
    output += f"Nama: `{result['server']['name']}`\n"
    output += f"Negara: `{result['server']['country']}, {result['server']['cc']}`\n"
    output += f"Sponsor: `{result['server']['sponsor']}`\n"
    output += f"Latensi: `{result['server']['latency']}`\n\n"
    output += "`Speed:`\n"
    output += f"Ping: `{result['ping']}`\n"
    output += f"Unduh: `{speed_convert(result['download'])}`\n"
    output += f"Unggah: `{speed_convert(result['upload'])}` "
    await spd.delete()
    await spd.client.send_message(spd.chat_id, output)


def speed_convert(size):
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@register(outgoing=True, pattern=r"^\.ping$")
async def pingme(pong):
    start = datetime.now()
    await pong.edit("**PONG!**")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit("**PONG!**\n`%sms`" % (duration))


@register(outgoing=True, pattern=r"^\.dc$")
async def neardc(event):
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(
        f"Negara : `{result.country}`\n"
        f"Pusat Data Terdekat : `{result.nearest_dc}`\n"
        f"Pusat Data ini : `{result.this_dc}`"
    )


CMD_HELP.update(
    {
        "speed": ">`.speed`" "\nUsage: Melakukan speedtest dan menunjukkan hasilnya.",
        "dc": ">`.dc`" "\nUsage: Menemukan pusat data terdekat dari server Anda.",
        "ping": ">`.ping`"
        "\nUsage: Menunjukkan berapa lama waktu yang dibutuhkan untuk melakukan ping ke bot Anda.",
    }
)
