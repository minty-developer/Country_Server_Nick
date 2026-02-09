import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True  # 멤버 이벤트 수신 필수

bot = commands.Bot(command_prefix="!", intents=intents)

# 기존 멤버에게 모든 역할 적용
async def apply_roles_to_member(member):
    roles = [r.name for r in member.roles if r.name != "@everyone"]
    if roles:
        new_nick = f"{member.name} [{' | '.join(roles)}]"
        try:
            await member.edit(nick=new_nick)
            print(f"Set nickname for {member} -> {new_nick}")
        except discord.Forbidden:
            print(f"Cannot change nickname for {member}")

# 서버 준비되면 기존 멤버 적용
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    for guild in bot.guilds:
        for member in guild.members:
            await apply_roles_to_member(member)

# 역할 추가/삭제 시 닉네임 자동 적용
@bot.event
async def on_member_update(before, after):
    # 역할이 바뀌었는지 확인
    if before.roles != after.roles:
        await apply_roles_to_member(after)

# 새로 들어온 멤버도 적용
@bot.event
async def on_member_join(member):
    await apply_roles_to_member(member)

bot.run(os.environ['DISCORD_TOKEN'])
