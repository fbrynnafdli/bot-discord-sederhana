import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime


# Muat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Periksa apakah token berhasil dimuat
if TOKEN is None:
    raise ValueError("Token tidak ditemukan. Pastikan file .env berisi variabel DISCORD_BOT_TOKEN.")

# Inisialisasi intents
intents = discord.Intents.default()
intents.message_content = True  # Intents untuk konten pesan
intents.voice_states = True #Intents untuk voice

# Global variable untuk melacak siapa yang mengundang bot ke chanel
inviter_id = None

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

# Perintah untuk merespons 'bajing'
@bot.command()
async def bajing(ctx):
    await ctx.send('batak anjing')

# Perintah untuk menampilkan avatar seseorang
@bot.command()
async def av(ctx, member: discord.Member = None):
    """Menampilkan avatar profil pengguna"""
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar {member.display_name}")
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def join(ctx):
    """Bergabung ke voice channel pengguna jika mereka ada di voice channel"""
    global inviter_id, empty_since
    if ctx.voice_client:  # Memeriksa apakah bot sudah berada di voice channel
        if ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("Saya sudah berada di voice channel yang sama dengan Baginda.")
        else:
            await ctx.send(f"Saya sudah berada di voice channel lain: {ctx.voice_client.channel.name}")
    else:
        if ctx.author.voice:  # Memeriksa apakah pengguna berada di voice channel
            channel = ctx.author.voice.channel
            await channel.connect()
            inviter_id = ctx.author.id  # Menyimpan ID pengguna yang mengundang bot
            empty_since = None  # Reset empty_since ketika bergabung
            await ctx.send(f"Saya telah bergabung ke {channel.name}")
            check_voice_channel.start()  # Mulai tugas periodik untuk memeriksa voice channel
        else:
            await ctx.send("Anda harus berada di voice channel terlebih dahulu!")

@bot.command()
async def leave(ctx):
    """Bot akan meninggalkan voice channel"""
    global inviter_id, empty_since
    if ctx.voice_client:  # Memeriksa apakah bot sedang berada di voice channel
        if ctx.author.id == inviter_id:  # Memeriksa apakah pengguna adalah pengundang bot
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Saya telah meninggalkan voice channel")
            song_queue.clear()
            inviter_id = None
            empty_since = None
            check_voice_channel.stop()  # Hentikan tugas periodik
        else:
            await ctx.send("Sedang digunakan oleh orang lain, tidak bisa meninggalkan.")
    else:
        await ctx.send("Saya tidak berada di voice channel manapun")

@tasks.loop(seconds=30)
async def check_voice_channel():
    """Cek voice channel setiap 30 detik, jika kosong selama 2 menit, bot akan keluar"""
    global empty_since
    for voice_client in bot.voice_clients:
        if voice_client and voice_client.is_connected():
            channel = voice_client.channel  # Mendapatkan channel dari voice_client
            if len(channel.members) == 1:  # Hanya bot yang ada di voice channel
                if empty_since is None:
                    empty_since = datetime.datetime.now(datetime.timezone.utc)
                elif (datetime.datetime.now(datetime.timezone.utc) - empty_since).total_seconds() > 120:  # 2 menit
                    await voice_client.disconnect()
                    empty_since = None
                    inviter_id = None
                    check_voice_channel.stop()  # Hentikan pengecekan jika sudah disconnect
            else:
                empty_since = None  # Reset ketika ada member yang masuk

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
    `!bajing` - Mengirim pesan "batak anjing"
    `!av` - Menampilkan avatar seseorang 
    `!join` - Mengundang Bot untuk masuk ke dalam voice chat
    `!leave` - Memerintahkan bot untuk meninggalkan voice chat
    `!help` - Menampilkan daftar perintah
    """
    await ctx.send(commands_list)

# Jalankan bot dengan token yang dimuat dari .env
bot.run(TOKEN)
