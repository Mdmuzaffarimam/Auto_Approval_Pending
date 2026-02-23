import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db


# ---------------- LOG ---------------- #
LOG_TEXT = """<b>#NewUser

ID - <code>{}</code>
Name - {}</b>
"""


# ---------------- START ---------------- #
@Client.on_message(filters.command("start"))
async def start_message(c, m):

    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(
            LOG_CHANNEL,
            LOG_TEXT.format(m.from_user.id, m.from_user.mention)
        )

    bot_username = (await c.get_me()).username

    caption = f"""<b>✨ Welcome {m.from_user.mention} ✨ @PendingXBot Join Request Bot

<blockquote>✅ Accept New Join Requests Instantly</blockquote>
<blockquote>🕒 Approve All Pending Requests Easily</blockquote>

📌 How To Get Started:

<blockquote>➊ Add me to your Channel or Group</blockquote>
<blockquote>➋ Give Admin Rights (Invite Users Permission)</blockquote>
<blockquote>➌ Use /accept to approve requests</blockquote>
━━━━━━━━━━━━━━━━━━━
🚀 Fast • Secure • Automatic</b>
"""

    await m.reply_photo(
        "https://graph.org/file/1a6f1d849376d47c1f305-5b83907d2bd289b0af.jpg",
        caption=caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add Me To Your Channel",
                        url=f"https://t.me/{bot_username}?startchannel=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ Add Me To Your Group",
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💝 Subscribe Channel",
                        url="https://t.me/Mrn_Officialx"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❣️ Developer",
                        url="https://t.me/mimam_officialx"
                    ),
                    InlineKeyboardButton(
                        "🌷 Update",
                        url="https://t.me/+u6qe756hjylkNmE1"
                    )
                ]
            ]
        )
    )


# ---------------- ACCEPT FUNCTION ---------------- #
async def approve_requests(acc, chat_id, msg):

    total = 0

    while True:
        try:
            await acc.approve_all_chat_join_requests(chat_id)

        except FloodWait as e:
            await asyncio.sleep(e.value)

        await asyncio.sleep(1)

        join_requests = [
            req async for req in
            acc.get_chat_join_requests(chat_id)
        ]

        total += len(join_requests)

        await msg.edit(
            f"**Processing…**\nAccepted: `{total}`"
        )

        if not join_requests:
            break

    await msg.edit(
        f"**✅ Done! Accepted All Requests**\n\nTotal: `{total}`"
    )


# ---------------- /ACCEPT ---------------- #
@Client.on_message(filters.command("accept") & filters.private)
async def accept(client, message):

    show = await message.reply("**Please Wait…**")

    user_data = await db.get_session(message.from_user.id)

    if user_data is None:
        return await show.edit(
            "**Login First Using /login**"
        )

    # Login user account
    try:
        acc = Client(
            "joinrequest",
            session_string=user_data,
            api_id=API_ID,
            api_hash=API_HASH
        )
        await acc.connect()

    except Exception:
        return await show.edit(
            "**Session Expired → Login Again**"
        )

    # -------- COMMAND ARGUMENT -------- #
    if len(message.command) > 1:

        ids = message.text.split()[1:]

        msg = await show.edit("**Processing IDs…**")

        for x in ids:
            try:
                chat_id = int(x)
                await approve_requests(acc, chat_id, msg)

            except Exception as e:
                await message.reply(
                    f"Failed For `{x}` → {e}"
                )

        return

    # -------- ASK INPUT -------- #
    await show.edit(
        "**Send Channel ID / Multiple IDs\n"
        "Or Forward Message From Channel**"
    )

    vj = await client.listen(message.chat.id)

    chat_ids = []

    # Forward
    if (
        vj.forward_from_chat
        and vj.forward_from_chat.type
        not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]
    ):
        chat_ids.append(vj.forward_from_chat.id)

    # Text IDs
    elif vj.text:
        for x in vj.text.split():
            try:
                chat_ids.append(int(x))
            except:
                pass

    else:
        return await message.reply("Invalid Input")

    await vj.delete()

    msg = await show.edit("**Starting Approval…**")

    for chat_id in chat_ids:
        await approve_requests(acc, chat_id, msg)


# ---------------- AUTO APPROVE NEW ---------------- #
@Client.on_chat_join_request(filters.group | filters.channel)
async def auto_approve(client, m):

    if NEW_REQ_MODE is False:
        return

    try:
        if not await db.is_user_exist(m.from_user.id):

            await db.add_user(
                m.from_user.id,
                m.from_user.first_name
            )

            await client.send_message(
                LOG_CHANNEL,
                LOG_TEXT.format(
                    m.from_user.id,
                    m.from_user.mention
                )
            )

        await client.approve_chat_join_request(
            m.chat.id,
            m.from_user.id
        )

        try:
            await client.send_message(
                m.from_user.id,
                f"""**Hello {m.from_user.mention}
Welcome To {m.chat.title}**"""
            )
        except:
            pass

    except Exception as e:
        print(e)
