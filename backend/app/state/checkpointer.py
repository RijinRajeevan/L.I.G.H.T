import os
import sqlite3
import logging
from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)

_conn = None
_checkpointer = None

def get_checkpointer():
    global _conn, _checkpointer
    if _checkpointer is None:
        try:
            db_path = "checkpoints.db"
            # Ensure connection is thread-safe and allows multiple instances if needed
            _conn = sqlite3.connect(db_path, check_same_thread=False)
            _checkpointer = SqliteSaver(_conn)
            logger.info("SqliteSaver checkpointer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize SqliteSaver: {e}")
            return None
    return _checkpointer
