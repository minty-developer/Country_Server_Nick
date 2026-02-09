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

MAX_NICK_LENGTH = 32  # Discord 닉네임 최대 길이

# ── 역할 기반 닉네임 적용 함수 ──
async def apply_roles_to_member(member):
    if member.guild.owner_id == member.id or member.bot:
        return

    # @everyone 제외, 가장 높은 역할만
    roles = [r for r in member.roles if r.name != "@everyone"]
    if roles:
        highest_role = max(roles, key=lambda r: r.position)
        new_nick = f"{member.display_name} [{highest_role.name}]"
    else:
        new_nick = member.display_name

    # 32자 제한 적용
    if len(new_nick) > MAX_NICK_LENGTH:
        new_nick = new_nick[:MAX_NICK_LENGTH]

    try:
        if member.nick != new_nick:
            await member.edit(nick=new_nick)
            logger.info(f"Nickname set: {member.display_name} -> {new_nick}")
    except discord.Forbidden:
        logger.warning(f"Cannot change nickname for {member.display_name} (Forbidden)")
    except discord.HTTPException as e:
        logger.error(f"HTTPException for {member.display_name}: {e}")

# ── 서버 준비되면 기존 멤버 적용 ──
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        logger.info(f"Processing guild: {guild.name} ({guild.id})")
        # 멤버 캐시 완전 로드
        await guild.chunk()
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
