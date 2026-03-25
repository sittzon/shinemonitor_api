import aiosqlite
import json
import os
from datetime import datetime
from typing import Optional, Any

DB_DIR = "/app/data"
DB_PATH = os.path.join(DB_DIR, "cache.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    return value

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ttl INTEGER
            )
        """)
        await db.commit()

async def get_cached(key: str) -> Optional[Any]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT value, timestamp, ttl FROM cache WHERE key = ?",
            (key,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        value, timestamp, ttl = row
        
        if ttl:
            cached_time = datetime.fromisoformat(timestamp)
            if (datetime.now() - cached_time).total_seconds() > ttl:
                await db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await db.commit()
                return None
        
        return json.loads(value)

async def set_cached(key: str, value: Any, ttl: Optional[int] = None):
    serialized = serialize_value(value)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO cache (key, value, timestamp, ttl) VALUES (?, ?, ?, ?)",
            (key, json.dumps(serialized), datetime.now().isoformat(), ttl)
        )
        await db.commit()

async def clear_cache():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cache")
        await db.commit()