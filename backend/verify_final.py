
import sqlite3
import requests
import json
import os

def verify():
    print("📋 Checking Database Tables...")
    db_path = 'backend/app/data/nyaya_vaani.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Found tables: {tables}")
        conn.close()
        
        if 'audit_logs' in tables:
            print("✅ 'audit_logs' table exists.")
        else:
            print("❌ 'audit_logs' table is MISSING.")

    print("\n🔍 Testing /analyze endpoint...")
    url = "http://localhost:8000/analyze"
    payload = {
        "text": "I need legal help with a land dispute",
        "session_id": "verify_final_script",
        "history": []
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            logs = data.get("agent_logs", [])
            print(f"Received {len(logs)} agent logs.")
            for log in logs:
                print(f"- {log.get('agent')}: {log.get('msg')[:100]}...")
            print("\n✅ Verification SUCCESSFUL.")
        else:
            print(f"❌ Verification FAILED with status {r.status_code}")
            print("Response:", r.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    verify()
