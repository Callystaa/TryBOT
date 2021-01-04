# Copyright (C) 2020 WAHYU TRY
# Deezload ported from Why
# Translated by Wahyu Try
# All rights reserved.

import asyncio
import glob
import os
import shutil
import subprocess
import time

import deezloader
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pylast import User
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo

from userbot import (
    CMD_HELP,
    DEEZER_ARL_TOKEN,
    LASTFM_USERNAME,
    TEMP_DOWNLOAD_DIRECTORY,
    bot,
    lastfm,
)
from userbot.events import register
from userbot.utils import chrome, progress


async def getmusic(cat):
    video_link = ""
    search = cat
    driver = await chrome()
    driver.get("https://www.youtube.com/results?search_query=" + search)
    user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
    for i in user_data:
        video_link = i.get_attribute("href")
        break
    command = f'youtube-dl --write-thumbnail --extract-audio --audio-format mp3 --audio-quality "320k" {video_link}'
    os.system(command)


async def getmusicvideo(cat):
    video_link = ""
    search = cat
    driver = await chrome()
    driver.get("https://www.youtube.com/results?search_query=" + search)
    user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
    for i in user_data:
        video_link = i.get_attribute("href")
        break
    command = 'youtube-dl -f "[filesize<50M]" --merge-output-format mp4 ' + video_link
    os.system(command)


@register(outgoing=True, pattern=r"^\.song (.*)")
async def _(event):
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
        await event.edit("`Wait..! Was looking for the song..`")
    elif reply.message:
        query = reply.message
        await event.edit("`I got it..! Prepare to upload songs..`")
    else:
        await event.edit("`What should i find?`")
        return

    await getmusic(str(query))
    l = glob.glob("*.mp3")
    loa = l[0]
    metadata = extractMetadata(createParser(loa))
    duration = 0
    if metadata.has("duration"):
        duration = metadata.get("duration").seconds
    performer = loa.split("-")[0][0:-1]
    title = loa.split("-")[1][1:]
    img_extensions = ["webp", "jpg", "jpeg", "webp"]
    img_filenames = [
        fn_img
        for fn_img in os.listdir()
        if any(fn_img.endswith(ext_img) for ext_img in img_extensions)
    ]
    thumb_image = img_filenames[0]
    await event.edit("`Okey.. Upload song..`")
    c_time = time.time()
    await event.client.send_file(
        event.chat_id,
        loa,
        attributes=[
            DocumentAttributeAudio(duration=duration, title=title, performer=performer)
        ],
        thumb=thumb_image,
        allow_cache=False,
        caption=query,
        reply_to=reply_to_id,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, event, c_time, "[UPLOAD]", loa)
        ),
    )
    await event.delete()
    os.system("rm -rf *.mp3")
    os.remove(thumb_image)
    subprocess.check_output("rm -rf *.mp3", shell=True)


@register(outgoing=True, pattern=r"^\.vsong(?: |$)(.*)")
async def _(event):
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
        await event.edit("`Wait..! I found the video of the song..`")
    elif reply:
        query = str(reply.message)
        await event.edit("`Wait..! I found the video of the song..`")
    else:
        await event.edit("`What should i find?`")
        return
    await getmusicvideo(query)
    l = glob.glob(("*.mp4")) + glob.glob(("*.mkv")) + glob.glob(("*.webm"))
    if l:
        await event.edit("`Yeah..! I found something..`")
    else:
        await event.edit(f"`Sorry:(..! I couldn't find anything with` **{query}**")
        return
    try:
        loa = l[0]
        metadata = extractMetadata(createParser(loa))
        duration = 0
        width = 0
        height = 0
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
        os.system("cp *mp4 thumb.mp4")
        os.system("ffmpeg -i thumb.mp4 -vframes 1 -an -s 480x360 -ss 5 thumb.jpg")
        thumb_image = "thumb.jpg"
        c_time = time.time()
        await event.client.send_file(
            event.chat_id,
            loa,
            force_document=False,
            thumb=thumb_image,
            allow_cache=False,
            caption=query,
            supports_streaming=True,
            reply_to=reply_to_id,
            attributes=[
                DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    round_message=False,
                    supports_streaming=True,
                )
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "[UPLOAD]", loa)
            ),
        )
        await event.edit(f"**{query}** `Upload success..!`")
        os.remove(thumb_image)
        os.system("rm *.mkv *.mp4 *.webm")
    except BaseException:
        os.remove(thumb_image)
        os.system("rm *.mkv *.mp4 *.webm")
        return


@register(outgoing=True, pattern=r"^\.smd (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit(
                "`Error: Tidak ada data scrobbling yang ditemukan.`"
            )
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@SpotifyMusicDownloaderBot"
    try:
        await event.edit("`Get the Music`")
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Download...`")
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=752979930)
                )
                msg = await bot.send_message(chat, track)
                respond = await response
                res = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=752979930)
                )
                r = await res
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("`Unblok `@SpotifyMusicDownloaderBot` dan coba lagi`")
                return
            await bot.forward_messages(event.chat_id, respond.message)
        await event.client.delete_messages(conv.chat_id, [msg.id, r.id, respond.id])
        await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@SpotifyMusicDownloaderBot` did not respond or song was not found!.`"
        )


@register(outgoing=True, pattern=r"^\.net (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit("`Error: No current scrobble found.`")
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@WooMaiBot"
    link = f"/netease {track}"
    await event.edit("`Search...`")
    try:
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Process... Please Wait`")
            try:
                msg = await conv.send_message(link)
                response = await conv.get_response()
                respond = await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("`Please unblok @WooMaiBot and try again`")
                return
            await event.edit("`Send the music...`")
            await asyncio.sleep(3)
            await bot.send_file(event.chat_id, respond)
        await event.client.delete_messages(
            conv.chat_id, [msg.id, response.id, respond.id]
        )
        await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@WooMaiBot` did not respond or song was not found!.`"
        )


@register(outgoing=True, pattern=r"^\.mhb(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit("`Enter a valid link to download from`")
    else:
        await event.edit("`Process...`")
    chat = "@MusicsHunterBot"
    try:
        async with bot.conversation(chat) as conv:
            try:
                msg_start = await conv.send_message("/start")
                response = await conv.get_response()
                msg = await conv.send_message(d_link)
                details = await conv.get_response()
                song = await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.edit("`Unblok `@MusicsHunterBot` dan coba lagi`")
                return
            await bot.send_file(event.chat_id, song, caption=details.text)
            await event.client.delete_messages(
                conv.chat_id, [msg_start.id, response.id, msg.id, details.id, song.id]
            )
            await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@MusicsHunterBot` did not respond or song was not found!.`"
        )


@register(outgoing=True, pattern=r"^\.deez (.+?|) (FLAC|MP3\_320|MP3\_256|MP3\_128)")
async def _(event):
    """DeezLoader by @An0nimia. Ported for UniBorg by @SpEcHlDe"""
    if event.fwd_from:
        return

    strings = {
        "name": "DeezLoad",
        "arl_token_cfg_doc": "ARL Token for Deezer",
        "invalid_arl_token": "please set the required variables for this module",
        "wrong_cmd_syntax": "bruh, now i think how far should we go. please terminate my Session.",
        "server_error": "We're experiencing technical difficulties.",
        "processing": "`Mengunduh...`",
        "uploading": "`Mengunggah...`",
    }

    ARL_TOKEN = DEEZER_ARL_TOKEN

    if ARL_TOKEN is None:
        await event.edit(strings["invalid_arl_token"])
        return

    try:
        loader = deezloader.Login(ARL_TOKEN)
    except Exception as er:
        await event.edit(str(er))
        return

    temp_dl_path = os.path.join(TEMP_DOWNLOAD_DIRECTORY, str(time.time()))
    if not os.path.exists(temp_dl_path):
        os.makedirs(temp_dl_path)

    required_link = event.pattern_match.group(1)
    required_qty = event.pattern_match.group(2)

    await event.edit(strings["processing"])

    if "spotify" in required_link:
        if "track" in required_link:
            required_track = loader.download_trackspo(
                required_link,
                output=temp_dl_path,
                quality=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
            )
            await event.edit(strings["uploading"])
            await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

        elif "album" in required_link:
            reqd_albums = loader.download_albumspo(
                required_link,
                output=temp_dl_path,
                quality=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
                zips=False,
            )
            await event.edit(strings["uploading"])
            for required_track in reqd_albums:
                await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

    elif "deezer" in required_link:
        if "track" in required_link:
            required_track = loader.download_trackdee(
                required_link,
                output=temp_dl_path,
                quality=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
            )
            await event.edit(strings["uploading"])
            await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

        elif "album" in required_link:
            reqd_albums = loader.download_albumdee(
                required_link,
                output=temp_dl_path,
                quality=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
                zips=False,
            )
            await event.edit(strings["uploading"])
            for required_track in reqd_albums:
                await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

    else:
        await event.edit(strings["wrong_cmd_syntax"])


async def upload_track(track_location, message):
    metadata = extractMetadata(createParser(track_location))
    duration = 0
    title = ""
    performer = ""
    if metadata.has("duration"):
        duration = metadata.get("duration").seconds
    if metadata.has("title"):
        title = metadata.get("title")
    if metadata.has("artist"):
        performer = metadata.get("artist")
    document_attributes = [
        DocumentAttributeAudio(
            duration=duration,
            voice=False,
            title=title,
            performer=performer,
            waveform=None,
        )
    ]
    supports_streaming = True
    force_document = False
    caption_rts = os.path.basename(track_location)
    c_time = time.time()
    await message.client.send_file(
        message.chat_id,
        track_location,
        caption=caption_rts,
        force_document=force_document,
        supports_streaming=supports_streaming,
        allow_cache=False,
        attributes=document_attributes,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, message, c_time, "[UPLOAD]"),
        ),
    )
    os.remove(track_location)


CMD_HELP.update(
    {
        "getmusic": ">`.song` **Artis - Judul Lagu**"
        "\nUsage: Menemukan dan mengunggah lagu.\n\n"
        ">`.vsong` **Artis - Judul Lagu**"
        "\nUsage: Menemukan dan mengunggah videoklip.\n\n"
        ">`.smd` **Artis - Judul Lagu**"
        "\nUsage: Unduh lagu dari Spotify menggunakan `@SpotifyMusicDownloaderBot`.\n\n"
        ">`.smd now`"
        "\nUsage: Unduh penggunaan scrobble LastFM saat ini menggunakan `@SpotifyMusicDownloaderBot`.\n\n"
        ">`.net` **Artis - Judul Lagu**"
        "\nUsage: Unduh lagu menggunakan `@WooMaiBot`.\n\n"
        ">`.net now`"
        "\nUsage: Unduh penggunaan scrobble LastFM saat ini menggunakan `@WooMaiBot`.\n\n"
        ">`.mhb <tautan Spotify/Deezer>`"
        "\nUsage: Unduh musik dari Spotify atau Deezer menggunakan `@MusicsHunterBot`.\n\n"
        ">`.deez` <tautan Spotify/Deezer> FORMAT\n"
        "Usage: Unduh musik dari Deezer atau Spotify.\n"
        "**Format** `FLAC`, `MP3_320`, `MP3_256`, `MP3_128`."
    }
)
