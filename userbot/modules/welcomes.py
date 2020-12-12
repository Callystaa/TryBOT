from datetime import datetime

from pytz import timezone
from telethon.events import ChatAction

from userbot import BOTLOG_CHATID, CLEAN_WELCOME, CMD_HELP, bot
from userbot.events import register


@bot.on(ChatAction)
async def welcome_to_chat(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import (
            get_current_welcome_settings,
            update_previous_welcome,
        )
    except AttributeError:
        return
    cws = get_current_welcome_settings(event.chat_id)
    if cws:
        """user_added=True,
        user_joined=True,
        user_left=False,
        user_kicked=False"""
        if (event.user_joined or event.user_added) and not (await event.get_user()).bot:
            if CLEAN_WELCOME:
                try:
                    await event.client.delete_messages(
                        event.chat_id, cws.previous_welcome
                    )
                except Exception as e:
                    LOGS.warn(str(e))
            a_user = await event.get_user()
            chat = await event.get_chat()
            me = await event.client.get_me()

            # Current time in UTC
            now_utc = datetime.now(timezone("UTC"))

            # Convert to Jakarta time zone
            jakarta_timezone = now_utc.astimezone(timezone("Asia/Jakarta"))
            if jakarta_timezone.hour < 4:
                time = "Selamat malam 🌒"
            elif 4 <= jakarta_timezone.hour < 6:
                time = "Selamat pagi 🌄"
            elif 6 <= jakarta_timezone.hour < 11:
                time = "Selamat pagi 🌄"
            elif 11 <= jakarta_timezone.hour < 13:
                time = "Selamat siang 🌤️"
            elif 13 <= jakarta_timezone.hour < 15:
                time = "Selamat siang 🌤️"
            elif 15 <= jakarta_timezone.hour < 18:
                time = "Selamat sore 🌅"
            elif 17 <= jakarta_timezone.hour < 19:
                time = "Selamat malam 🌙"
            else:
                time = "Selamat malam 🌕"

            title = chat.title if chat.title else "this chat"
            participants = await event.client.get_participants(chat)
            count = len(participants)
            mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
            my_mention = "[{}](tg://user?id={})".format(me.first_name, me.id)
            first = a_user.first_name
            last = a_user.last_name
            fullname = f"{first} {last}" if last else first
            username = f"@{a_user.username}" if a_user.username else mention
            userid = a_user.id
            my_first = me.first_name
            my_last = me.last_name
            my_fullname = f"{my_first} {my_last}" if my_last else my_first
            my_username = f"@{me.username}" if me.username else my_mention
            file_media = None
            current_saved_welcome_message = None
            if cws:
                if cws.f_mesg_id:
                    msg_o = await event.client.get_messages(
                        entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
                    )
                    file_media = msg_o.media
                    current_saved_welcome_message = msg_o.message
                elif cws.reply:
                    current_saved_welcome_message = cws.reply
            current_message = await event.reply(
                current_saved_welcome_message.format(
                    mention=mention,
                    time=time,
                    title=title,
                    count=count,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                ),
                file=file_media,
            )
            update_previous_welcome(event.chat_id, current_message.id)


@register(outgoing=True, pattern=r"^\.setwelcome(?: |$)(.*)")
async def save_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import add_welcome_setting
    except AttributeError:
        return await event.edit("`Running on Non-SQL mode!`")
    msg = await event.get_reply_message()
    string = event.pattern_match.group(1)
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#WELCOME_NOTE \nCHAT ID: {event.chat_id}"
                "\nPesan berikut ini disimpan sebagai pesan pembuka baru "
                "untuk obrolan, JANGAN hapus !!",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
            )
            msg_id = msg_o.id
        else:
            return await event.edit(
                "`Untuk menyimpan media sebagai bagian dari pesan pembuka, BOTLOG_CHATID harus disetel.`"
            )
    elif event.reply_to_msg_id and not string:
        rep_msg = await event.get_reply_message()
        string = rep_msg.text
    success = "`Pesan sambutan {} untuk obrolan ini.`"
    if add_welcome_setting(event.chat_id, 0, string, msg_id) is True:
        await event.edit(success.format("disimpan"))
    else:
        await event.edit(success.format("diupdate"))


@register(outgoing=True, pattern=r"^\.checkwelcome$")
async def show_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import get_current_welcome_settings
    except AttributeError:
        return await event.edit("`Running on Non-SQL mode!`")
    cws = get_current_welcome_settings(event.chat_id)
    if not cws:
        return await event.edit(
            "`Tidak ada pesan selamat datang yang disimpan di sini.`"
        )
    elif cws.f_mesg_id:
        msg_o = await event.client.get_messages(
            entity=BOTLOG_CHATID, ids=int(cws.f_mesg_id)
        )
        await event.edit(
            "`Saat ini saya menyambut pengguna baru dengan catatan selamat datang ini.`"
        )
        await event.reply(msg_o.message, file=msg_o.media)
    elif cws.reply:
        await event.edit(
            "`Saat ini saya menyambut pengguna baru dengan catatan selamat datang ini.`"
        )
        await event.reply(cws.reply)


@register(outgoing=True, pattern=r"^\.rmwelcome$")
async def del_welcome(event):
    try:
        from userbot.modules.sql_helper.welcome_sql import rm_welcome_setting
    except AttributeError:
        return await event.edit("`Running on Non-SQL mode!`")
    if rm_welcome_setting(event.chat_id) is True:
        await event.edit("`Catatan selamat datang dihapus untuk obrolan ini.`")
    else:
        await event.edit("`Apakah saya punya pesan selamat datang di sini ?`")


CMD_HELP.update(
    {
        "welcome": ">`.setwelcome <pesan selamat datang> atau membalas pesan dengan .setwelcome`"
        "\nUsage: Menyimpan pesan sebagai catatan selamat datang di obrolan."
        "\n\nVariabel yang tersedia untuk memformat pesan selamat datang :"
        "\n`{mention}, {time}, {title}, {count}, {first}, {last}, {fullname}, "
        "{userid}, {username}, {my_first}, {my_fullname}, {my_last}, "
        "{my_mention}, {my_username}`"
        "\n\n>`.checkwelcome`"
        "\nUsage: Periksa apakah Anda memiliki catatan selamat datang di obrolan."
        "\n\n>`.rmwelcome`"
        "\nUsage: Menghapus catatan selamat datang untuk obrolan saat ini."
    }
)
