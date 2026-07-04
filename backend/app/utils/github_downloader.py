import requests
import os
import json
import pandas as pd

# URLs to try
CANDIDATES = [
    {
        "url": "https://raw.githubusercontent.com/mrvivacious/Indian-Penal-Code/master/IPC.csv",
        "format": "csv",
        "filename": "ipc.csv"
    },
    {
        "url": "https://raw.githubusercontent.com/civictech-India/Indian-Law-Penal-Code-Json/master/data.json",
        "format": "json",
        "filename": "ipc.json"
    },
    {
        "url": "https://raw.githubusercontent.com/anoopk/indian-penal-code/master/ipc.csv",
        "format": "csv",
        "filename": "ipc.csv"
    }
]

DATA_DIR = "backend/app/data/ipc"

def download_ipc():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    for candidate in CANDIDATES:
        print(f"⬇️ Trying {candidate['url']}...")
        try:
            response = requests.get(candidate['url'], timeout=10)
            if response.status_code == 200:
                print(f"✅ Success! Downloading...")
                
                kv_path = os.path.join(DATA_DIR, candidate['filename'])
                with open(kv_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify content
                if candidate['format'] == 'csv':
                    df = pd.read_csv(kv_path)
                    print(f"📊 Downloaded {len(df)} rows.")
                    # Standardize columns if needed? 
                    # For now just save.
                elif candidate['format'] == 'json':
                    with open(kv_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"📊 Downloaded JSON with {len(data)} entries.")
                    # Convert to CSV for consistency?
                    # Let's keep as JSON if that's what we got, but LegalAgent needs update.
                    
                print(f"💾 Saved to {kv_path}")
                return candidate['format'], candidate['filename']
            else:
                print(f"❌ Failed: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

    return None, None

if __name__ == "__main__":
    fmt, fname = download_ipc()
    if fmt:
        print(f"🎉 IPC Dataset Ready: {fname} ({fmt})")
    else:
        print("💀 All downloads failed.")
