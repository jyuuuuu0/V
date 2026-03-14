from discord.ext import commands

class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="도움말")
    async def help(self, ctx):
        await ctx.send("""
📖 **명령어 목록**

`!todo` — 오늘 팀원 전체 할 일 목록 조회
`!prlist` — 리뷰 대기 중인 PR 목록 조회
`!scrumstats` — 내 스크럼 완료율 통계
`!도움말` — 명령어 목록 안내
""")