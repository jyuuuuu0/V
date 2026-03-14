from discord.ext import commands
import aiosqlite
import datetime

class Todo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def todo(self, ctx):
        today = str(datetime.date.today())

        async with aiosqlite.connect("scrum.db") as db:
            cursor = await db.execute(
                "SELECT user_id, task FROM todos WHERE date=?",
                (today,)
            )
            rows = await cursor.fetchall()

        if not rows:
            await ctx.send("오늘 할 일이 없습니다.")
            return

        guild = ctx.guild
        lines = []
        for r in rows:
            member = guild.get_member(int(r[0]))
            name = member.display_name if member else f"<{r[0]}>"
            lines.append(f"{name}: {r[1]}")

        text = "\n".join(lines)
        await ctx.send(f"📋 오늘 할 일\n{text}")