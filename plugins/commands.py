```python
import asyncio
from pyrogram import Client, filters
from config import LOG_CHANNEL, API_ID, API_HASH, NEW_REQ_MODE
from plugins.database import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= LOG TEXT =================

LOG_TEXT = """<b>#NewUser
    
ID - <code>{}</code>

Nᴀᴍᴇ - {}</b>
"""

# ================= START =================

@Client.on_message(filters.command('start') & filters.private)
async def start_message(c, m):

    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(
            LOG_CHANNEL,
            LOG_TEXT.format(m.from_user.id, m.from_user.mention)
        )

    await m.reply_photo(
        "https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=(
            f"<b>Hello {m.from_user.mention} 👋\n\n"
            "I Am Join Request Acceptor Bot.\n"
            "I Can Accept All Old Pending Join Request.\n\n"
            "👉 Use /accept in Channel</b>"
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        '💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ᴄʜᴀɴɴᴇʟ',
                        url='https://t.me/Mrn_Officialx'
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ",
                        url='https://t.me/mimam_officialx'
                    ),
                    InlineKeyboardButton(
                        "🌷 ᴜᴘᴅᴀᴛᴇ",
                        url='https://t.me/+u6qe756hjylkNmE1'
                    )
                ]
            ]
        )
    )

# ================= ACCEPT OLD REQUESTS =================

@Client.on_message(filters.command('accept') & (filters.channel | filters.group))
async def accept(client, message):

    show = await message.reply("**Please Wait.....**")

    # Get user session
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        return await show.edit(
            "**First Login In Bot PM Using /login**"
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
    except:
        return await show.edit(
            "**Session Expired.\nLogout & Login Again.**"
        )

    chat_id = message.chat.id

    msg = await show.edit(
        "**Accepting all pending join requests...**"
    )

    try:
        while True:

            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)

            join_requests = [
                req async for req in
                acc.get_chat_join_requests(chat_id)
            ]

            if not join_requests:
                break

        await msg.edit(
            "**✅ Successfully Accepted All Pending Requests.**"
        )

    except Exception as e:
        await msg.edit(f"**Error:** `{str(e)}`")

# ================= AUTO ACCEPT NEW =================

@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):

    if NEW_REQ_MODE == False:
        return

    try:
        # Save user in DB
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

        # Approve request
        await client.approve_chat_join_request(
            m.chat.id,
            m.from_user.id
        )

        # Welcome message
        try:
            await client.send_message(
                m.from_user.id,
                f"**Hello {m.from_user.mention}!\n"
                f"Welcome To {m.chat.title}\n\n"
                "__Powered By : @Mrn_Officialx__**"
            )
        except:
            pass

    except Exception as e:
        print(str(e))
```
