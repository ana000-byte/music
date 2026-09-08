import discord
from discord.ext import commands
import yt_dlp
import asyncio
from flask import Flask
from threading import Thread
import os

# --- نظام إبقاء البوت مستيقظاً لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "Music Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# إعدادات تحميل الصوت من يوتيوب
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': False, 'quiet': True}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

# تخزين طابور الأغاني لكل سيرفر
queues = {}

async def play_next(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        next_song = queues[ctx.guild.id].pop(0)
        url = next_song['url']
        title = next_song['title']
        
        source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source, after=lambda: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"🎶 الآن يتم تشغيل: **{title}**")
    else:
        await ctx.send("انتهت قائمة الانتظار! 💤")

@bot.event
async def on_ready():
    print(f'✅ Bot is ready! Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, *, search):
    """تشغيل أغنية عبر البحث في يوتيوب"""
    if not ctx.author.voice:
        return await ctx.send("❌ يجب أن تكون في قناة صوتية أولاً!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                url = info['url']
                title = info['title']
            except Exception:
                return await ctx.send("❌ لم أجد هذه الأغنية!")

        if ctx.voice_client.is_playing():
            if ctx.guild.id not in queues: queues[ctx.guild.id] = []
            queues[ctx.guild.id].append({'url': url, 'title': title})
            await ctx.send(f"✅ تمت إضافة **{title}** للطابور.")
        else:
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            await ctx.send(f"🎶 جاري تشغيل: **{title}**")

@bot.command()
async def skip(ctx):
    """تخطي الأغنية الحالية"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ تم التخطي!")
    else:
        await ctx.send("لا يوجد شيء لتخطيه.")

@bot.command()
async def queue(ctx):
    """عرض قائمة الانتظار"""
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        list_songs = "\n".join([f"{i+1}. {s['title']}" for i, s in enumerate(queues[ctx.guild.id])])
        await ctx.send(f"📜 **قائمة الانتظار:**\n{list_songs}")
    else:
        await ctx.send("قائمة الانتظار فارغة.")

@bot.command()
async def stop(ctx):
    """إيقاف كل شيء ومغادرة القناة"""
    if ctx.guild.id in queues: queues[ctx.guild.id] = []
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("تم إغلاق المشغل ومغادرة القناة. 👋")

keep_alive()
import os
# ... باقي الكود ...
bot.run(os.getenv('BOT_TOKEN'))

