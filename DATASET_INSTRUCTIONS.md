# NYAYA-VAANI Dataset Setup (Flexible)

I am unable to verify specific Kaggle links due to access restrictions. 
**Please find ANY dataset that matches these descriptions and place them as instructed.**

## 1. Indian Penal Code (IPC)
**Goal**: Get the text of IPC Sections.
1.  Go to [Kaggle](https://www.kaggle.com/) and search for: `Indian Penal Code` or `IPC Sections`.
2.  Download **ANY** CSV that looks like it has "Section" and "Description" columns.
    - *Example Search*: `divymodi12/indain-ipc-sections`
3.  **Rename** the file to: `ipc.csv`
4.  **Place in**: `backend/app/data/ipc/`

## 2. Bharatiya Sakshya Adhiniyam (BSA)
**Goal**: Get the text of the new Evidence Act.
1.  Search Kaggle/Google for: `Bharatiya Sakshya Adhiniyam` or `BSA 2023`.
2.  Download PDF or CSV.
3.  **Place in**: `backend/app/data/bsa/`

## 3. Case Laws / Judgments
**Goal**: Get past Supreme Court/High Court judgments.
1.  Search Kaggle for: `Indian Supreme Court Judgments` or `Indian Case Law`.
    - *Example Search*: `Indian Kanoon`
2.  Download the dataset.
3.  **Place in**: `backend/app/data/case_laws/`

## 4. FIR Data (Optional - Large)
**Goal**: Get real crime reports.
1.  Search Kaggle for: `Crime in India` or `FIR Dataset`.
2.  **Place in**: `backend/app/data/fir/`

---
**Verification**
After placing the files, simply restart the backend or tell me "I'm done", and the agents will try to auto-detect the columns!
