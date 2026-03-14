# db.py
import aiosqlite

DB_NAME = "scrum.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS scrum (
            user_id TEXT,
            date TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            user_id TEXT,
            task TEXT,
            date TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS scrum_threads (
            date TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS completion (
            user_id TEXT,
            date TEXT,
            completed INTEGER,
            task TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS prs (
            pr_number TEXT,
            title TEXT,
            url TEXT,
            approved INTEGER,
            created_at TEXT
        )
        """)
        await db.commit()