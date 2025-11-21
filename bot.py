import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import google.generativeai as genai

# Muat variabel lingkungan dari file .env
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Periksa apakah token berhasil dimuat
if TOKEN is None:
    raise ValueError("Token tidak ditemukan. Pastikan file .env berisi variabel DISCORD_BOT_TOKEN.")
if GEMINI_KEY is None:
    raise ValueError("GEMINI_API_KEY tidak ditemukan. Pastikan file .env berisi variabel GEMINI_API_KEY.")

# Inisialisasi intents
intents = discord.Intents.default()
intents.message_content = True  # Intents untuk konten pesan
intents.voice_states = True #Intents untuk voice
intents.members = True

# Global variable untuk melacak siapa yang mengundang bot ke chanel
inviter_id = None

# Inisialisasi bot dengan prefix '!' dan intents, dan menonaktifkan help command bawaan
bot = commands.Bot(command_prefix='v', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    print("\n--- MULAI DIAGNOSIS GEMINI ---")
    
    # 1. Cek apakah API Key terbaca
    GEMINI_KEY_CHECK = os.getenv('GEMINI_API_KEY')
    if GEMINI_KEY_CHECK:
        # Tampilkan 5 huruf depan saja biar aman, sisanya bintang
        print(f"STATUS API KEY: Terbaca ({GEMINI_KEY_CHECK[:5]}******)")
    else:
        print("STATUS API KEY: GAWAT! Key terbaca sebagai 'None' atau Kosong!")

    # 2. Cek Model yang Tersedia
    print("Mencoba menghubungi Google untuk minta daftar model...")
    try:
        import google.generativeai as genai
        # Pastikan configure dipanggil lagi disini untuk memastikan
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- Model Ditemukan: {m.name}")
    except Exception as e:
        print(f"ERROR saat nge-list model: {e}")
        
    print("--- DIAGNOSIS SELESAI ---\n")
# Command Custom
@bot.command()
async def woy(ctx):
    await ctx.send('apa ngentot')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def bajing(ctx):
    await ctx.send('batak anjing')

@bot.command()
async def ulangi(ctx, *, message: str):
    await ctx.send(message)

# Command General
@bot.command()
async def av(ctx, member: discord.Member = None):
    """Menampilkan avatar profil pengguna"""
    member = member or ctx.author
    embed = discord.Embed(title=f"Avatar {member.display_name}")
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

# Command Server Info
@bot.command()
async def info(ctx):
    await ctx.send(f'Server ini mempunyai {ctx.guild.member_count} orang dongo!')

# Command Moderation
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name='Muted')

    if not role:
        role = await guild.create_role(name='Muted', permissions=discord.Permissions(send_messages=False, add_reactions=False))

        for channel in guild.channels:
            await channel.set_permissions(role, send_messages=False, add_reactions=False)

    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.mention} telah di muted. alasan: {reason if reason else "tanpa alasan"}')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} telah di unmuted.')
    else:
        await ctx.send(f'{member.mention} sedang tidak di muted.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} telah di ban. alasan: {reason if reason else "tanpa alasan"}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f'{user.mention} telah di unbanned.')

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} telah di mute. alasan: {reason if reason else "tanpa alasan"}')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member: discord.Member, time: str, *, reason=None):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not role:
        role = await ctx.guild.create_role(name='Muted', permissions=discord.Permissions(send_messages=False, add_reactions=False))
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, add_reactions=False)

    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.mention} telah di mute sementara hingga {time}. Reason: {reason if reason else "tanpa alasan"}')

    time_mapping = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if time[-1] in time_mapping:
        duration = int(time[:-1]) * time_mapping[time[-1]]
    else:
        await ctx.send("Invalid time format. Use a format like 10m, 1h, or 1d.")
        return

    await asyncio.sleep(duration)
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} waktu unmute telah selesai.')

# Command Music Player
@bot.command()
async def join(ctx):
    """Bergabung ke voice channel pengguna jika mereka ada di voice channel"""
    global inviter_id, empty_since
    if ctx.voice_client:  # Memeriksa apakah bot sudah berada di voice channel
        if ctx.voice_client.channel == ctx.author.voice.channel:
            await ctx.send("Saya sudah berada di voice channel yang sama dengan Baginda.")
        else:
            await ctx.send(f"Saya sudah berada di voice channel lain, tidak bisa bergabung")
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
            inviter_id = None
            empty_since = None
            check_voice_channel.stop()
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

@bot.command()
async def tanya(ctx, *, pertanyaan):
    """Bertanya kepada Vot AI"""
    # Kasih tahu user kalau bot lagi mikir (typing...)
    async with ctx.typing():
        try:
            # Minta Vot AI mikir
            response = model.generate_content(pertanyaan)
            text = response.text

            # Discord punya batas 2000 huruf per pesan.
            # Kalau jawaban Vot AI kepanjangan, kita pecah.
            if len(text) > 2000:
                for i in range(0, len(text), 2000):
                    await ctx.send(text[i:i+2000])
            else:
                await ctx.send(text)
        except Exception as e:
            await ctx.send(f"Aduh, otak saya error: {e}")

# Command untuk menampilkan daftar perintah
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Vot Command List",
        color=0x00FFFF
    )
    
    embed.add_field(name="General", value="`afk` `avatar` `help` `ping`", inline=True)
    embed.add_field(name="Info Server", value="`info`", inline=True)
    embed.add_field(name="Moderation", value="`ban` `mute` `kick` `tempmute` `unban` `unmute`", inline=True)
    embed.add_field(name="Command Custom", value="`woy` `bajing` `ping` `ulangi`")
    await ctx.send(embed=embed)
    
# Jalankan bot dengan token yang dimuat dari .env
bot.run(TOKEN)