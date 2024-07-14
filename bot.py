import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Muat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Periksa apakah token berhasil dimuat
if TOKEN is None:
    raise ValueError("Token tidak ditemukan. Pastikan file .env berisi variabel DISCORD_BOT_TOKEN.")

# Inisialisasi intents
intents = discord.Intents.default()
intents.message_content = True  # Intents untuk konten pesan

# Inisialisasi bot dengan prefix '!' dan intents, dan menonaktifkan help command bawaan
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Perintah sederhana untuk menguji bot
@bot.command()
async def hello(ctx):
    await ctx.send('apa anjing')

# Perintah untuk merespons 'woy'
@bot.command()
async def woy(ctx):
    await ctx.send('apa ngentot')

# Perintah  untuk merespons 'ping'
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Perintah  untuk merespons 'info'
@bot.command()
async def info(ctx):
    await ctx.send(f'Server ini mempunyai {ctx.guild.member_count} orang dongo!')

# Perintah untuk merespons 'ulangi' yang mengulangi pesan pengguna
@bot.command()
async def ulangi(ctx, *, message: str):
    await ctx.send(message)

# Perintah untuk merespons 'p'
@bot.command()
async def p(ctx):
    await ctx.send('pa pe pa pe')

# Perintah kustom untuk menampilkan daftar perintah
@bot.command()
async def help(ctx):
    commands_list = """
    Berikut adalah command yang tersedia:
    `!hello` - Mengirim pesan 'apa anjing!'
    `!woy` - Mengirim pesan 'apa ngentot'
    `!ping` - Mengirim pesan 'Pong!'
    `!info` - Menampilkan jumlah orang dongo di server ini
    `!echo [message]` - Mengulangi pesan yang diberikan
    `!p` - Mengirim pesan 'pa pe pa pe'
    `!help` - Menampilkan daftar perintah
    """
    await ctx.send(commands_list)

# Jalankan bot dengan token yang dimuat dari .env
bot.run(TOKEN)
