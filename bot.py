import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import aiosqlite
import datetime
from db import init_db 

from scheduler import start_scheduler
from commands.todo import Todo
from commands.pr_list import PRList
from commands.stats import Stats
from commands.help import Help

load_dotenv(override=True)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.add_cog(Todo(bot))
    await bot.add_cog(PRList(bot))
    await bot.add_cog(Stats(bot))
    await bot.add_cog(Help(bot))
    await init_db()
    print(f"{bot.user} 실행됨")
    start_scheduler(bot)


# 스크럼 작성 감지
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    today = str(datetime.date.today())

    if isinstance(message.channel, discord.Thread):
        async with aiosqlite.connect("scrum.db") as db:
            await db.execute(
                "INSERT INTO scrum (user_id, date) VALUES (?,?)",
                (str(message.author.id), today)
            )
            await db.commit()

        # 오늘 할 일 파싱
        lines = message.content.split("\n")
        for i, line in enumerate(lines):
            if "오늘 할 일" in line:
                # "2. 오늘 할 일: 이슈 남기기" 처럼 같은 줄에 있는 경우
                if ":" in line:
                    task = line.split(":", 1)[1].strip()
                    if task:
                        async with aiosqlite.connect("scrum.db") as db:
                            await db.execute(
                                "INSERT INTO todos (user_id, task, date) VALUES (?,?,?)",
                                (str(message.author.id), task, today)
                            )
                            await db.commit()

        await message.add_reaction("✅")

    await bot.process_commands(message)


# 완료 여부 체크
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) not in ["⭕", "❌"]:
        return

    today = str(datetime.date.today())
    completed = 1 if str(reaction.emoji) == "⭕" else 0

    # 해당 유저의 오늘 할 일 가져오기
    async with aiosqlite.connect("scrum.db") as db:
        cursor = await db.execute(
            "SELECT task FROM todos WHERE user_id=? AND date=?",
            (str(user.id), today)
        )
        row = await cursor.fetchone()
        task = row[0] if row else ""

        await db.execute(
            "INSERT INTO completion (user_id, date, completed, task) VALUES (?,?,?,?)",
            (str(user.id), today, completed, task)
        )
        await db.commit()
        

bot.run(TOKEN)