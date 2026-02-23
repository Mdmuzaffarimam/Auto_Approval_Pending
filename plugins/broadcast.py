from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked, PeerIdInvalid
from plugins.database import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return "Success"

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)

    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Deleted Account Removed")
        return "Deleted"

    except UserIsBlocked:
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Blocked Bot")
        return "Blocked"

    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - PeerIdInvalid Removed")
        return "Error"

    except Exception as e:
        logger.error(f"Broadcast Error to {user_id}: {e}")
        return "Error"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):

    users = await db.get_all_users()
    total_users = await db.total_users_count()

    b_msg = message.reply_to_message
    sts = await message.reply_text("🚀 Broadcasting started...")

    start_time = time.time()

    done = 0
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    async for user in users:
        user_id = user.get("id")

        if not user_id:
            failed += 1
            done += 1
            continue

        result = await broadcast_messages(int(user_id), b_msg)

        if result == "Success":
            success += 1
        elif result == "Blocked":
            blocked += 1
        elif result == "Deleted":
            deleted += 1
        else:
            failed += 1

        done += 1

        # 🔥 Rate limit safety
        await asyncio.sleep(0.05)

        # Update progress every 25 users
        if done % 25 == 0:
            await sts.edit(
                f"📢 Broadcast In Progress...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Success: {success}\n"
                f"🚫 Blocked: {blocked}\n"
                f"🗑 Deleted: {deleted}\n"
                f"❌ Failed: {failed}\n"
                f"📊 Completed: {done}/{total_users}"
            )

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    await sts.edit(
        f"✅ Broadcast Completed!\n\n"
        f"⏱ Time Taken: {time_taken}\n\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Success: {success}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🗑 Deleted: {deleted}\n"
        f"❌ Failed: {failed}"
    )
