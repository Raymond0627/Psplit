# Lumeed Psplit (Super-Optimized PDF QR & Barcode Splitter)

A high-performance Windows desktop application and standalone executable to automatically split multi-page scanned PDF documents using barcode or QR separator sheets (e.g., sheets with `DOCSEP`, QR codes, Code 128, Code 39, etc.).

Inspired by `adlerweb/PdfQRSplit`, re-engineered from the ground up for extreme speed, zero disk churn, and an intuitive modern GUI.

---

## ⚡ Key Improvements over Original PdfQRSplit

| Feature | Original PdfQRSplit | Lumeed Psplit |
| :--- | :--- | :--- |
| **Decoding Speed** | Slow Python/Java ZXing wrapper via subprocess | **Native C++ `zxing-cpp`** (20x-50x faster) |
| **Disk I/O** | Writes intermediate PNG files to disk per page | **100% In-Memory RAM buffer** (Zero disk writes) |
| **PDF Extraction** | PyPDF4 (broken object references, raster glitches) | **PyMuPDF (MuPDF C engine)** (Lossless, instant range extraction) |
| **Multi-Core** | Single-threaded | **Parallel Multi-Core page scanning** |
| **Supported Barcodes** | QR / basic barcodes | **QR Codes, Code 128, Code 39, EAN, DataMatrix** |
| **Interface** | CLI only | **Modern Desktop GUI + Full CLI support** |
| **Distribution** | Requires Python, Pip, Java, Pillow | **Standalone Windows `.exe` & Setup Installer** |

---

## 🚀 Installation & Running

### Option 1: Run Setup Installer (`Setup.exe`)
Download or run:
```
dist/installer/Lumeed_Psplit_Setup.exe
```
This installs Lumeed Psplit to your computer with a Desktop shortcut and Start Menu entry.

### Option 2: Portable Executable
Run directly without installing:
```
dist/Lumeed_Psplit/Lumeed_Psplit.exe
```

---

## 🖥️ Using the GUI

1. **Input PDF:** Click **Browse File** to select your multi-page scanned PDF document.
2. **Output Folder:** Select the destination directory (defaults to `split_output/` next to your PDF).
3. **Separator Text:** Enter your separator keyword (e.g. `DOCSEP`).
4. **Match Type:**
   - `contains` (default): Triggers split if the barcode content contains the text.
   - `exact`: Exact match.
   - `regex`: Custom regular expression pattern.
5. **Separator Page Handling:**
   - **`discard`** *(Default)*: Separator sheets are excluded from output documents.
   - **`keep_prev`**: Separator sheet is retained at the end of the preceding document.
   - **`keep_next`**: Separator sheet is retained at the beginning of the following document.
6. **Naming Pattern:** Customize file names with format tokens:
   - `{original_name}_part_{index:03d}`
   - Supported variables: `{original_name}`, `{index}`, `{total_splits}`, `{start_page}`, `{end_page}`.
7. Click **Start Splitting**. View real-time progress and logs, then click **Open Output Folder**.

---

## 💻 Command Line Interface (CLI)

The tool can also be run directly from PowerShell or Command Prompt for automated batch processing:

```powershell
# Using the python script:
python main.py input.pdf -s DOCSEP -m discard -o ./output

# Or with custom pattern and match type:
python main.py input.pdf -s "DOCSEP" --match exact --pattern "{original_name}_doc_{index:02d}"
```

CLI Arguments:
- `input`: Path to input PDF file.
- `-o, --output`: Output directory (default: `split_output`).
- `-s, --separator`: Separator text (default: `DOCSEP`).
- `-m, --mode`: Separator page handling (`discard`, `keep_prev`, `keep_next`).
- `--match`: Barcode matching method (`contains`, `exact`, `regex`).
- `--pattern`: Output filename template.
- `--dpi`: Rendering DPI for barcode detection (default: `150`).
- `-q, --quiet`: Quiet mode.

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
- Standalone folder: `dist/Lumeed_Psplit/Lumeed_Psplit.exe`
- Setup wizard installer: `dist/installer/Lumeed_Psplit_Setup.exe`
