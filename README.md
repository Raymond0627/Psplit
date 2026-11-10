# Folio (Super-Optimized PDF QR & Barcode Separator)

A modern, high-performance desktop application and Windows installer to automatically split multi-page scanned PDF documents using barcode or QR separator sheets (e.g. sheets with `DOCSEP`, QR codes, Code 128, Code 39, etc.).

Re-engineered from the ground up for extreme speed, zero disk churn, and a beautiful minimalist interface.

---

## ⚡ Key Highlights

| Feature | Description |
| :--- | :--- |
| **Decoding Speed** | **Native C++ `zxing-cpp`** (20x-50x faster, zero disk writes) |
| **PDF Extraction** | **PyMuPDF (MuPDF C engine)** (Lossless, instant range extraction) |
| **Multi-Core** | **Parallel multi-core page scanning** |
| **Supported Barcodes** | **QR Codes, Code 128, Code 39, EAN, DataMatrix** |
| **Interface** | **Modern minimalist light/dark desktop GUI** + CLI support |
| **Distribution** | **Standalone Windows `.exe` & Setup Installer** |

---

## 🚀 Installation & Running

### Option 1: Run Setup Installer (`Setup.exe`)
Download or run:
```
dist/installer/Folio_Setup.exe
```
This installs Folio to your computer with a Desktop shortcut and Start Menu entry.

### Option 2: Portable Executable
Run directly without installing:
```
dist/Folio/Folio.exe
```

---

## 🖥️ Using the GUI

1. **Input PDF:** Click **Browse** to select your multi-page scanned PDF document.
2. **Output Folder:** Select the destination directory (defaults to `split_output/` next to your PDF).
3. **Separator Text:** Enter your separator keyword (e.g. `DOCSEP`).
4. **Match Type:**
   - `contains` (default): Triggers split if the barcode content contains the text.
   - `exact`: Exact match.
   - `regex`: Custom regular expression pattern.
5. **Separator Page Handling:**
   - **`Discard`** *(Default)*: Separator sheets are excluded from output documents.
   - **`Keep previous`**: Separator sheet is retained at the end of the preceding document.
   - **`Keep next`**: Separator sheet is retained at the beginning of the following document.
6. **Naming Pattern:** Customize file names with format tokens:
   - `{original_name}_part_{index:03d}`
   - Supported variables: `{original_name}`, `{index}`, `{total_splits}`, `{start_page}`, `{end_page}`.
7. Click **Start splitting**. View real-time progress, then click **Open folder**.

---

## 💻 Command Line Interface (CLI)

The tool can also be run directly from PowerShell or Command Prompt for automated batch processing:

```powershell
python main.py input.pdf -s DOCSEP -m discard -o ./output
```

---

## 🛠️ Building & Developing from Source

### 1. Requirements
- Python 3.10+
- Install dependencies:
  ```powershell
  pip install -r requirements.txt
  ```

### 2. Run Tests
```powershell
python -m pytest tests/ -v
```

### 3. Rebuild Executable & Installer
```powershell
python build_exe.py
```
This generates:
- Standalone folder: `dist/Folio/Folio.exe`
- Setup wizard installer: `dist/installer/Folio_Setup.exe`
