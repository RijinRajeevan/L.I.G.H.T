
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.db.database import engine, Base
from app.db.models import AuditLog, EscalationQueue # Import to register with Base

async def init_db_fixed():
    print("🚀 Initializing Database with all models...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(init_db_fixed())
