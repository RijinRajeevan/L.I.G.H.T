"""
PolicySyncAgent — Autonomous Legal Knowledge Base Updater
=========================================================
This agent runs on a daily schedule and autonomously:
  1. Scrapes official Indian government legislative portals for changes
     (India Code, MCA, UIDAI, RTO, etc.)
  2. Detects new/amended sections using a diff-based hash comparison
  3. Uses an LLM to summarise and categorise each change
  4. Upserts the updated entries into the ChromaDB vector store
  5. Sends an audit log entry recording what was changed and why

"""

import os
import time
import json
import hashlib
import logging
import datetime
from typing import List, Dict, Optional

# ─── Optional imports (install separately if running standalone) ───────────────
try:
    import requests
    from bs4 import BeautifulSoup
    from sentence_transformers import SentenceTransformer
    import chromadb
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("[PolicySyncAgent] WARNING: Dependencies not installed. Run: pip install requests beautifulsoup4")

logger = logging.getLogger("PolicySyncAgent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


# ──────────────────────────────────────────────────────────────────────────────
# 1. Configuration — Government Portals to Monitor
# ──────────────────────────────────────────────────────────────────────────────

POLICY_SOURCES = [
    {
        "name": "India Code — IPC",
        "url": "https://www.indiacode.nic.in/handle/123456789/2263",
        "category": "ipc",
        "selector": "div.simple-col",        # CSS selector for section listing
        "change_indicator": "Amendment Acts"
    },
    {
        "name": "India Code — BNS (Bharatiya Nyaya Sanhita 2023)",
        "url": "https://www.indiacode.nic.in/handle/123456789/20062",
        "category": "bsa",
        "selector": "div.simple-col",
        "change_indicator": "Notified On"
    },
    {
        "name": "UIDAI — Aadhaar Regulations",
        "url": "https://uidai.gov.in/en/about-uidai/legal-framework/gazette-notifications.html",
        "category": "civic",
        "selector": "div.notification-list",
        "change_indicator": "Gazette Notification"
    },
    {
        "name": "Ministry of Road Transport — MV Act Amendments",
        "url": "https://morth.nic.in/acts-rules",
        "category": "civic",
        "selector": "ul.notifications",
        "change_indicator": "Motor Vehicles"
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# 2. Change Detection — Hash-based diffing
# ──────────────────────────────────────────────────────────────────────────────

HASH_CACHE_PATH = os.path.join(os.path.dirname(__file__), ".policy_hash_cache.json")


def load_hash_cache() -> Dict[str, str]:
    """Load previously stored content hashes to detect changes."""
    if os.path.exists(HASH_CACHE_PATH):
        with open(HASH_CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def save_hash_cache(cache: Dict[str, str]):
    """Persist updated hashes after a sync run."""
    with open(HASH_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def compute_content_hash(content: str) -> str:
    """SHA-256 hash of page content for change detection."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ──────────────────────────────────────────────────────────────────────────────
# 3. Web Scraper — Fetches and parses government pages
# ──────────────────────────────────────────────────────────────────────────────

def fetch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch raw HTML from a government portal with a browser-like User-Agent."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CIVIA-PolicyBot/1.0; +https://civia.gov.app)",
        "Accept-Language": "en-IN,en;q=0.9"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_sections(html: str, css_selector: str) -> List[Dict]:
    """
    Parse page HTML and extract individual legal section entries.
    Returns a list of dicts with 'section' and 'description' keys.
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.select(css_selector)

    sections = []
    for block in blocks:
        text = block.get_text(separator=" ", strip=True)
        if len(text) < 20:  # Skip noise
            continue

        # Heuristic: detect section numbers like "Section 302" or "S.302" or "IPC 302"
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            if any(kw in line for kw in ["Section", "Sec.", "IPC", "BNS", "Act", "Rule"]):
                sections.append({
                    "section": line[:80],
                    "description": text[:500],
                })
                break

    return sections


# ──────────────────────────────────────────────────────────────────────────────
# 4. LLM Summariser — Compresses and categorises new legal text
# ──────────────────────────────────────────────────────────────────────────────

def summarise_change_with_llm(old_text: str, new_text: str, section_name: str) -> str:
    """
    Uses Groq (Llama 3.1) to produce a structured summary of what changed
    and why it matters to Indian citizens.
    """
    try:
        from groq import Groq
        from dotenv import load_dotenv

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(BASE_DIR, ".env"))

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are a legal analyst for Indian law. A government policy section has changed.

SECTION: {section_name}

OLD TEXT:
{old_text[:800] if old_text else "(New addition — no previous version)"}

NEW TEXT:
{new_text[:800]}

In 2-3 sentences, explain:
1. What changed (specific amendment or addition).
2. How this affects Indian citizens practically.

Be precise and factual. No speculation.
"""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert Indian legal analyst. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=256,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"LLM summarisation failed: {e}")
        return new_text[:300]  # Fallback: store raw text


# ──────────────────────────────────────────────────────────────────────────────
# 5. Vector DB Upsert — Updates ChromaDB with changed sections
# ──────────────────────────────────────────────────────────────────────────────

def upsert_to_vector_db(collection_name: str, section_id: str, description: str, section_label: str):
    """
    Embeds the new/updated section and upserts it into ChromaDB.
    Uses the same embedding model as the main application for consistency.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "chroma_db")

    try:
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Failed to load SentenceTransformer in PolicySyncAgent: {e}")
        return
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    embedding = embedding_model.encode([description])[0].tolist()

    collection.upsert(
        ids=[section_id],
        embeddings=[embedding],
        documents=[description],
        metadatas=[{
            "section": section_label,
            "source": collection_name,
            "last_updated": datetime.datetime.utcnow().isoformat(),
            "auto_synced": "true"
        }]
    )
    logger.info(f"Upserted section '{section_label}' into collection '{collection_name}'")


# ──────────────────────────────────────────────────────────────────────────────
# 6. Audit Log — Records every sync event for transparency
# ──────────────────────────────────────────────────────────────────────────────

AUDIT_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "policy_sync_audit.jsonl"
)


def write_audit_log(event: dict):
    """Append-only JSONL audit log for every change detected and processed."""
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        **event
    }
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    logger.info(f"Audit logged: {entry['event']}")


# ──────────────────────────────────────────────────────────────────────────────
# 7. Main Sync Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_policy_sync():
    """
    Core sync loop:
    - For each configured government source:
        1. Fetch the page
        2. Compare hash with cache → skip if unchanged
        3. Extract updated sections
        4. LLM-summarise the changes
        5. Upsert into ChromaDB
        6. Audit log every change
    """
    if not DEPS_AVAILABLE:
        logger.error("Required dependencies missing. Install: pip install requests beautifulsoup4")
        return

    logger.info("=" * 60)
    logger.info("PolicySyncAgent — Starting daily knowledge base sync")
    logger.info(f"Monitoring {len(POLICY_SOURCES)} government portals")
    logger.info("=" * 60)

    hash_cache = load_hash_cache()
    total_changes = 0

    for source in POLICY_SOURCES:
        logger.info(f"\n→ Checking: {source['name']}")

        html = fetch_page(source["url"])
        if not html:
            write_audit_log({"event": "FETCH_FAILED", "source": source["name"]})
            continue

        content_hash = compute_content_hash(html)
        cached_hash = hash_cache.get(source["url"])

        if content_hash == cached_hash:
            logger.info(f"  ✓ No changes detected since last sync.")
            continue

        logger.info(f"  ⚡ Change detected! Processing updated sections...")

        # Extract sections
        sections = extract_sections(html, source["selector"])
        logger.info(f"  Found {len(sections)} sections to process")

        for sec in sections[:20]:  # Process max 20 per source per run
            section_id = f"{source['category']}_{hashlib.md5(sec['section'].encode()).hexdigest()[:12]}"
            old_description = ""   # In production: retrieve from DB for diffing

            # LLM summarise
            summary = summarise_change_with_llm(old_description, sec["description"], sec["section"])

            # Upsert to vector DB
            try:
                upsert_to_vector_db(
                    collection_name=source["category"],
                    section_id=section_id,
                    description=summary,
                    section_label=sec["section"]
                )
                total_changes += 1

                write_audit_log({
                    "event": "SECTION_UPDATED",
                    "source": source["name"],
                    "section": sec["section"],
                    "section_id": section_id,
                    "summary_preview": summary[:120]
                })

            except Exception as e:
                logger.error(f"  Failed to upsert section '{sec['section']}': {e}")
                write_audit_log({
                    "event": "UPSERT_FAILED",
                    "source": source["name"],
                    "section": sec["section"],
                    "error": str(e)
                })

        # Update hash cache
        hash_cache[source["url"]] = content_hash
        save_hash_cache(hash_cache)

    logger.info("\n" + "=" * 60)
    logger.info(f"PolicySyncAgent — Sync complete. {total_changes} changes processed.")
    logger.info("=" * 60)

    write_audit_log({
        "event": "SYNC_COMPLETE",
        "total_changes": total_changes,
        "sources_checked": len(POLICY_SOURCES)
    })


# ──────────────────────────────────────────────────────────────────────────────
# 8. Scheduler — Runs automatically every 24 hours
# ──────────────────────────────────────────────────────────────────────────────

def start_scheduled_sync(interval_hours: int = 24):
    """
    Blocking loop that runs the policy sync on a fixed interval.
    In production, this would run as a separate Docker container or Lambda function.

    Usage:
        python -m app.agents.policy_sync_agent
    """
    logger.info(f"PolicySyncAgent scheduler started. Interval: every {interval_hours} hours.")
    logger.info("Press Ctrl+C to stop.")

    while True:
        run_policy_sync()
        next_run = datetime.datetime.now() + datetime.timedelta(hours=interval_hours)
        logger.info(f"Next sync scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(interval_hours * 3600)


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Run once immediately when executed directly, then schedule
    start_scheduled_sync(interval_hours=24)
