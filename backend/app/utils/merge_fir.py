import pandas as pd
import os
import glob

# Path configuration
FIR_DIR = "backend/app/data/fir"
OUTPUT_FILE = os.path.join(FIR_DIR, "fir.csv")

def merge_fir_datasets():
    print("🔄 Starting FIR Dataset Merge...")
    
    # Get all CSV files in the directory
    all_files = glob.glob(os.path.join(FIR_DIR, "*.csv"))
    
    # Filter out the output file itself if it exists
    all_files = [f for f in all_files if f != OUTPUT_FILE]
    
    if not all_files:
        print("❌ No FIR CSV files found to merge.")
        return

    print(f"📦 Found {len(all_files)} files to merge.")
    
    combined_csv = pd.DataFrame()
    
    for file in all_files:
        try:
            print(f"   - Reading {os.path.basename(file)}...")
            # Try different encodings
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding='latin1')
            
            # Add a 'Source_File' column to track origin
            df['Source_Dataset'] = os.path.basename(file)
            
            combined_csv = pd.concat([combined_csv, df], ignore_index=True)
        except Exception as e:
            print(f"   ⚠️ Failed to read {file}: {e}")

    # Save merged file
    if not combined_csv.empty:
        combined_csv.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"✅ Successfully merged {len(combined_csv)} records into '{OUTPUT_FILE}'")
        print(f"   - Columns: {list(combined_csv.columns)}")
    else:
        print("❌ Merge resulted in empty dataset.")

if __name__ == "__main__":
    merge_fir_datasets()
