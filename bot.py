import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

# قراءة بيانات الاتصال من متغيرات البيئة في Koyeb
API_ID = int(os.getenv("37064763", "0"))
API_HASH = os.getenv("A9871c1a1f463927b6b8020411e510105", "")
BOT_TOKEN = os.getenv("8713363251:AAF6q1h51G-AscBcuxkHsueZXtH6sKYIw7A", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

# إعداد العميل الأساسي للبوت والحساب المساعد
app = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "Assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call_py = PyTgCalls(assistant)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await message.reply(
        "أهلاً بك! أنا بوت تشغيل الموسيقى في المكالمات الصوتية.\n\n"
        "أضفني إلى مجموعتك وارفعني (مشرف) لكي أتمكن من العمل، ثم استخدم الأمر:\n"
        "`/play اسم_الأغنية` للتشغيل."
    )

@app.on_message(filters.command("play") & filters.group)
async def play_music(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ يرجى كتابة اسم الأغنية بجانب الأمر، مثال:\n`/play عمرو دياب`")
    
    query = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    
    status_msg = await message.reply("🔄 جاري البحث والاتصال بالمكالمة الصوتية...")
    
    try:
        ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not query.startswith("http"):
                search_query = f"ytsearch:{query}"
            else:
                search_query = query
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            stream_url = info['url']
            title = info.get('title', 'مقطوعة صوتية')

        await call_py.join_group_call(
            chat_id,
            AudioPiped(stream_url)
        )
        await status_msg.edit(f"🎶 جاري الآن تشغيل:\n**{title}**")
    except Exception as e:
        await status_msg.edit(f"❌ حدث خطأ أثناء التشغيل:\n`{str(e)}`")

@app.on_message(filters.command("stop") & filters.group)
async def stop_music(client: Client, message: Message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply("⏹ تم إيقاف الموسيقى ومغادرة المكالمة الصوتية.")
    except Exception as e:
        await message.reply(f"خطأ: {str(e)}")

async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    print("تم تشغيل البوت بنجاح!")
    await asyncio.gather(app.idle(), assistant.idle())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
