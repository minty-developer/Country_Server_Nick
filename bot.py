import discord
from discord.ext import commands
import os
import logging

# ── Logging 설정 ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bot')

# ── Intents ──
intents = discord.Intents.default()
intents.members = True  # 멤버 이벤트 필수

bot = commands.Bot(command_prefix="!", intents=intents)

# ── 역할 기반 닉네임 적용 함수 ──
async def apply_roles_to_member(member):
    if member.guild.owner_id == member.id or member.bot:
        return

    roles = [r.name for r in member.roles if r.name != "@everyone"]
    if roles:
        new_nick = f"{member.name} [{' | '.join(roles)}]"
    else:
        new_nick = member.name

    try:
        if member.nick != new_nick:
            await member.edit(nick=new_nick)
            logger.info(f"Nickname set: {member} -> {new_nick}")
    except discord.Forbidden:
        logger.warning(f"Cannot change nickname for {member} (Forbidden)")
    except discord.HTTPException as e:
        logger.error(f"HTTPException for {member}: {e}")

# ── 서버 준비되면 기존 멤버 테스트 적용 ──
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        logger.info(f"Processing guild: {guild.name} ({guild.id})")
        if guild.members:
            logger.info(f"First member test: {guild.members[0]} | roles: {[r.name for r in guild.members[0].roles]}")
        else:
            logger.warning("No members found!")

        for member in guild.members:
            await apply_roles_to_member(member)
    logger.info("All existing members processed.")

# ── 역할 변경 이벤트 ──
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        await apply_roles_to_member(after)

# ── 새 멤버 접속 이벤트 ──
@bot.event
async def on_member_join(member):
    await apply_roles_to_member(member)

# ── 봇 실행 ──
bot.run(os.environ['DISCORD_TOKEN'])
