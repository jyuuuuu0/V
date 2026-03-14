from flask import Flask, request
import requests
import os

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


@app.route("/github", methods=["POST"])
def github():
    data = request.json

    if data["action"] == "opened":
        pr = data["pull_request"]

        msg = f"""
📌 새로운 PR

제목: {pr["title"]}
작성자: {pr["user"]["login"]}

{pr["html_url"]}
"""
        requests.post(DISCORD_WEBHOOK, json={"content": msg})

        # PR DB 저장
        import asyncio
        asyncio.run(save_pr(pr))

    return "", 200


async def save_pr(pr):
    import aiosqlite
    import datetime
    async with aiosqlite.connect("scrum.db") as db:
        await db.execute(
            "INSERT INTO prs VALUES (?,?,?,?,?)",
            (str(pr["number"]), pr["title"], pr["html_url"], 0,
             str(datetime.datetime.now()))
        )
        await db.commit()
app.run(port=5000) 