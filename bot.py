import asyncio
import os
from aiohttp import web

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN


# 🌐 Auto PORT detect (Koyeb / Heroku)
PORT = int(os.environ.get("PORT", 8080))


class Bot(Client):

    def __init__(self):
        super().__init__(
            "vj join request bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):

        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username

        print('Bot Started Powered By @VJ_Botz')

        # ✅ Web server start for health check
        await self.start_web_server()

    async def stop(self, *args):

        await super().stop()
        print('Bot Stopped Bye')

    # 🌐 Web server function
    async def start_web_server(self):

        async def root(request):
            return web.Response(text="Bot Running ✅")

        app = web.Application()
        app.router.add_get("/", root)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        print(f"Web Server Started On Port {PORT}")


# ▶️ Run Bot
Bot().run()
