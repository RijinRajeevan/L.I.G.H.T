import os
import sys

# --- Configuration ---
# Get absolute path to backend/.env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, '.env')
DATA_DIR = os.path.join(BASE_DIR, 'app', 'data')

# Load env vars BEFORE importing kaggle
from dotenv import load_dotenv
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    print(f"📄 Loaded .env from {ENV_PATH}")
else:
    print(f"⚠️ .env not found at {ENV_PATH}")
    
# Now import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi

DATASETS = {
    "ipc": "libindra/indian-penal-code-ipc-dataset",
    # "fir": "libindra/karnataka-police-fir-dataset", # Too large, times out
    "bsa": "sohamshashank/bharatiya-sakshya-adhiniyam-bsa",
    # "case_laws": "libindra/supreme-court-of-india-judgment-dataset", # Large
}

def setup_kaggle_api():
    """Authenticates using environment variables."""
    # Check for credentials
    if not os.getenv("KAGGLE_USERNAME") or not os.getenv("KAGGLE_KEY"):
        print("❌ KAGGLE_USERNAME or KAGGLE_KEY not found in environment.")
        return None

    api = KaggleApi()
    try:
        api.authenticate()
        print("✅ Kaggle API Authenticated successfully.")
        return api
    except Exception as e:
        print(f"❌ Authentication Failed: {e}")
        return None

def download_and_extract(api, dataset_slug, extract_path):
    """Downloads and extracts a dataset."""
    print(f"⬇️ Downloading {dataset_slug} to {extract_path}...")
    try:
        api.dataset_download_files(dataset_slug, path=extract_path, unzip=True)
        print(f"✅ Downloaded and extracted to {extract_path}")
        # List files
        files = os.listdir(extract_path)
        print(f"📄 Files in {extract_path}: {files}")
        if not files:
            print(f"⚠️ Warning: Directory is empty after download!")
    except Exception as e:
        print(f"❌ Failed to download {dataset_slug}: {e}")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📁 Created data directory: {DATA_DIR}")

    api = setup_kaggle_api()
    if not api:
        return

    for key, slug in DATASETS.items():
        dataset_path = os.path.join(DATA_DIR, key)
        if not os.path.exists(dataset_path):
             os.makedirs(dataset_path)
        
        # Check if already populated
        if len(os.listdir(dataset_path)) > 0:
            print(f"ℹ️ {key} dataset already exists in {dataset_path}, skipping.")
            continue
            
        download_and_extract(api, slug, dataset_path)

    print("\n🎉 All datasets processed.")

if __name__ == "__main__":
    main()
