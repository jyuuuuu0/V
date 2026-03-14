from discord.ext import commands
import aiosqlite

class PRList(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prlist(self, ctx):

        async with aiosqlite.connect("scrum.db") as db:

            cursor = await db.execute(
                "SELECT pr_number, title FROM prs WHERE approved=0"
            )

            rows = await cursor.fetchall()

        if not rows:
            await ctx.send("리뷰 대기 PR이 없습니다.")
            return

        text = "\n".join([f"#{r[0]} {r[1]}" for r in rows])

        await ctx.send(f"📌 리뷰 대기 PR\n{text}")