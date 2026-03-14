from discord.ext import commands
import aiosqlite


class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scrumstats(self, ctx):

        async with aiosqlite.connect("scrum.db") as db:
            cursor = await db.execute("""
                SELECT
                    SUM(CASE WHEN completed=1 THEN 1 ELSE 0 END) as done,
                    SUM(CASE WHEN completed=0 THEN 1 ELSE 0 END) as not_done
                FROM completion
                WHERE user_id=?
            """, (str(ctx.author.id),))
            row = await cursor.fetchone()

        if not row or row[0] is None or (row[0] + row[1]) == 0:
            await ctx.send("통계 데이터가 없습니다.")
            return

        done = row[0]
        not_done = row[1]
        total = done + not_done
        rate = int((done / total) * 100)

        await ctx.send(f"📊 {ctx.author.display_name}님의 스크럼 통계\n완료율 {rate}% ({done}⭕ / {not_done}❌)")