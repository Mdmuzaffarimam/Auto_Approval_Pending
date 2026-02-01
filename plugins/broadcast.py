from pyrogram import Client, filters
from pyrogram.errors import (
    InputUserDeactivated,
    FloodWait,
    UserIsBlocked,
    PeerIdInvalid
)

from plugins.database import db
from config import ADMINS

import asyncio
import datetime
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def broadcast_messages(user_id: int, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)

    except InputUserDeactivated:
        await db.delete_user(user_id)
        logger.info(f"{user_id} removed (Deleted Account)")
        return False, "Deleted"

    except UserIsBlocked:
        await db.delete_user(user_id)
        logger.info(f"{user_id} removed (Blocked Bot)")
        return False, "Blocked"

    except PeerIdInvalid:
        await db.delete_user(user_id)
        logger.info(f"{user_id} removed (Invalid ID)")
        return False, "Invalid"

    except Exception as e:
        logger.error(f"Temporary error for {user_id}: {e}")
        return False, "TempError"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    b_msg = message.reply_to_message

    sts = await message.reply_text("📢 Broadcasting messages...")

    start_time = time.time()

    done = success = blocked = deleted = invalid = failed = 0

    async for user in users:
        user_id = user.get("id")

        if not user_id:
            failed += 1
            done += 1
            continue

        status, reason = await broadcast_messages(int(user_id), b_msg)

        if status:
            success += 1
        else:
            if reason == "Blocked":
                blocked += 1
            elif reason == "Deleted":
                deleted += 1
            elif reason == "Invalid":
                invalid += 1
            else:
                failed += 1

        done += 1

        # speed control
        await asyncio.sleep(0.05)

        if done % 20 == 0:
            await sts.edit(
                f"📊 Broadcast in progress\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Success: {success}\n"
                f"🚫 Blocked: {blocked}\n"
                f"🗑 Deleted: {deleted}\n"
                f"❌ Invalid: {invalid}\n"
                f"⚠ Failed: {failed}\n\n"
                f"⏳ Progress: {done}/{total_users}"
            )

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    await sts.edit(
        f"✅ Broadcast Completed\n\n"
        f"⏱ Time Taken: {time_taken}\n"
        f"👥 Total Users: {total_users}\n\n"
        f"✅ Success: {success}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🗑 Deleted: {deleted}\n"
        f"❌ Invalid: {invalid}\n"
        f"⚠ Failed: {failed}"
    )
