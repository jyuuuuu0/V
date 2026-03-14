import discord
from discord.ext import tasks
import datetime
import os
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

def start_scheduler(bot):

    @tasks.loop(minutes=1)
    async def scheduler():
        now = datetime.datetime.now()
        channel = bot.get_channel(CHANNEL_ID)

        # 오전 8시 스크럼 생성
        if now.hour == 8 and now.minute == 0:
            async with aiosqlite.connect("scrum.db") as db:
                cursor = await db.execute(
                    "SELECT 1 FROM scrum_threads WHERE date=?", (str(now.date()),)
                )
                if not await cursor.fetchone():
                    await create_scrum(bot)

        # 12:40 미작성 리마인드
        if now.hour == 12 and now.minute == 40:
            await remind_missing(channel)

        # 23:00 마감 리마인드
        if now.hour == 23 and now.minute == 0:
            await closing(channel)

        # 매 정각, 30분마다 PR 리마인드 체크
        if now.minute == 0 or now.minute == 30:
            await remind_pr(channel)

    scheduler.start()


async def create_scrum(bot):
    forum_channel = bot.get_channel(CHANNEL_ID)
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    thread_name = f"데일리 스크럼 - {today}"

    incomplete_text = ""
    async with aiosqlite.connect("scrum.db") as db:
        cursor = await db.execute(
            "SELECT user_id, task FROM completion WHERE date=? AND completed=0",
            (yesterday,)
        )
        rows = await cursor.fetchall()

    if rows:
        guild = bot.get_guild(int(os.getenv("GUILD_ID")))
        lines = []
        for r in rows:
            member = guild.get_member(int(r[0]))
            name = member.display_name if member else f"<{r[0]}>"
            lines.append(f"{name}: {r[1]}")
        incomplete_text = f"\n⚠ 어제 미완료 항목\n" + "\n".join(lines) + "\n"

    content = f"""
```[데일리 스크럼 - 날짜]

1. 어제 한 일
2. 오늘 할 일
3. 이슈 / 도움 필요한 점
{incomplete_text}
```
오늘 할 일을 완료하면 ⭕
못하면 ❌ 리액션을 눌러주세요.
"""

    await forum_channel.create_thread(name=thread_name, content=content)

    async with aiosqlite.connect("scrum.db") as db:
        await db.execute(
            "INSERT INTO scrum_threads (date) VALUES (?)", (str(today),)
        )
        await db.commit()


async def remind_missing(channel):
    today = str(datetime.date.today())

    async with aiosqlite.connect("scrum.db") as db:
        cursor = await db.execute(
            "SELECT user_id FROM scrum WHERE date=?",
            (today,)
        )
        rows = await cursor.fetchall()

    if not rows:
        await channel.send("⚠ 아직 데일리 스크럼 작성자가 없습니다.")


async def closing(channel):
    await channel.send(
        "\n⏰ 오늘 업무 종료까지 1시간 남았습니다\n\n오늘 할 일을 마무리해주세요!\n"
    )


async def remind_pr(channel):
    now = datetime.datetime.now()

    async with aiosqlite.connect("scrum.db") as db:
        cursor = await db.execute(
            "SELECT pr_number, title, url, created_at FROM prs WHERE approved=0"
        )
        rows = await cursor.fetchall()

    if not rows:
        return

    lines = []
    for r in rows:
        created_at = datetime.datetime.fromisoformat(r[3])
        diff = now - created_at

        if diff.total_seconds() >= 7200:  # 2시간 이상
            lines.append(f"⏰ #{r[0]} {r[1]} - {int(diff.total_seconds() // 3600)}시간째 리뷰 대기 중\n{r[2]}")
    if lines:
        text = "\n\n".join(lines)
        fe_role_id = os.getenv("FE_ROLE_ID")
        await channel.send(f"<@&{fe_role_id}> 📌 리뷰가 필요한 PR\n{text}")