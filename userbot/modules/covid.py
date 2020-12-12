# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port to UserBot by @MoveAngel

from covid import Covid

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.covid(?: |$)(.*)")
async def corona(event):
    await event.edit("`Mengambil data...`")
    query = event.pattern_match.group(1)
    if query:
        country = query
    else:
        country = "world"
    covid = Covid(source="worldometers")
    try:
        country_data = covid.get_status_by_country_name(country)
        output_text = (
            f"`ℹ️ Dikonfirmasi    : {format_integer(country_data['confirmed'])}`\n"
            + f"`😁 Hidup          : {format_integer(country_data['active'])}`\n"
            + f"`⚰️ Meninggal      : {format_integer(country_data['deaths'])}`\n"
            + f"`💉 Dipulihkan     : {format_integer(country_data['recovered'])}`\n\n"
            + f"`💼 Kasus Baru     : {format_integer(country_data['new_cases'])}`\n"
            + f"`😵 Kematian Baru  : {format_integer(country_data['new_deaths'])}`\n"
            + f"`🤕 Kritis         : {format_integer(country_data['critical'])}`\n"
            + f"`📝 Tes Total      : {format_integer(country_data['total_tests'])}`\n\n"
            + f"🌐 Data disediakan oleh [Worldometer](https://www.worldometers.info/coronavirus/country/{country})"
        )
        await event.edit(f"Info Virus Corona di {country}:\n\n{output_text}")
    except ValueError:
        await event.edit(
            f"Tidak ada informasi yang ditemukan untuk: {country}!\nPeriksa ejaan Anda dan coba lagi."
        )


def format_integer(number, thousand_separator="."):
    def reverse(string):
        string = "".join(reversed(string))
        return string

    s = reverse(str(number))
    count = 0
    result = ""
    for char in s:
        count = count + 1
        if count % 3 == 0:
            if len(s) == count:
                result = char + result
            else:
                result = thousand_separator + char + result
        else:
            result = char + result
    return result


CMD_HELP.update(
    {
        "covid": ">`.covid` **negara**"
        "\nUsage: Dapatkan informasi tentang data covid-19 di negara Anda.\n"
    }
)
