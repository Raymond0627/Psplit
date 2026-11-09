# PDF QR/Barcode Splitter Desktop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a super-optimized local PDF QR/Barcode separator tool with a modern desktop UI and standalone Windows `.exe` installer/distribution.

**Architecture:** High-speed in-memory pipeline using PyMuPDF (C-based MuPDF) for page rendering/lossless extraction and `zxing-cpp` (native C++) for barcode scanning, parallelized across CPU cores, wrapped in a modern GUI and packaged with PyInstaller.

**Tech Stack:** Python 3, PyMuPDF, zxing-cpp, Pillow, CustomTkinter, PyInstaller, pytest.

**Spec:** `docs/superpowers/specs/2026-11-04-pdf-qr-splitter-design.md`

## Global Constraints
- Zero disk temporary file writes during barcode detection.
- Must support both 1D barcodes (Code 128, Code 39) and 2D barcodes (QR Code).
- Lossless page extraction (preserves text layers, vector fidelity, metadata).
- Clean, standalone Windows executable packaging.

## Review Focus
1. Empty PDF or 0-page input handled gracefully without crashing.
2. PDF without any separator barcodes outputs a single identical copy or clear notice.
3. Separator appearing on page 1 handled properly in `discard`, `keep_prev`, and `keep_next` modes.
4. Consecutive separator pages (e.g., page 3 and 4 both separators) handled without producing empty files.
5. Invalid/corrupted PDF files report a clear error message instead of an unhandled crash.

---

### Task 1: Environment Setup & Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/ui/__init__.py`

- [ ] **Step 1: Create requirements.txt**
Define dependencies: `PyMuPDF>=1.23.0`, `zxing-cpp>=2.2.0`, `Pillow>=10.0.0`, `customtkinter>=5.2.0`, `pytest>=7.0.0`, `pyinstaller>=6.0.0`.
- [ ] **Step 2: Install dependencies in the Python environment**
Run: `pip install -r requirements.txt`
- [ ] **Step 3: Verify core imports**
Run: `python -c "import fitz, zxingcpp, PIL, customtkinter; print('Imports successful')"`
- [ ] **Step 4: Commit scaffolding**

---

### Task 2: Core Barcode & QR Detection Engine (`src/core/scanner.py`)

**Files:**
- Create: `src/core/scanner.py`
- Create: `tests/test_scanner.py`

**Interfaces:**
- Produces: `scan_page(doc_path: str, page_num: int, dpi: int = 150) -> List[str]` (returns detected barcode text strings on the page)

- [ ] **Step 1: Write test with synthetic test image / PDF containing barcode**
Create helper to generate a sample 1-page PDF containing a QR code / Code 128 barcode ("DOCSEP") and assert `scan_page(...)` returns `["DOCSEP"]`.
- [ ] **Step 2: Implement `src/core/scanner.py`**
Implement memory-only rendering via `page.get_pixmap(dpi=dpi)` and decode via `zxingcpp.read_barcodes(image)`.
- [ ] **Step 3: Run pytest on scanner**
Run: `pytest tests/test_scanner.py -v`
Expected: PASS
- [ ] **Step 4: Commit scanner module**

---

### Task 3: Lossless Splitter & Parallel Orchestrator (`src/core/splitter.py`)

**Files:**
- Create: `src/core/splitter.py`
- Create: `tests/test_splitter.py`

**Interfaces:**
- Consumes: `src/core/scanner.py`
- Produces: `class PdfSplitter`
  - Method: `split(pdf_path, output_dir, separator_text="DOCSEP", mode="discard", match_type="contains", naming_pattern="{original_name}_part_{index:03d}", progress_callback=None) -> SplitResult`

- [ ] **Step 1: Write tests for edge cases**
Test `discard`, `keep_prev`, `keep_next`, consecutive separators, and first-page separator.
- [ ] **Step 2: Implement `PdfSplitter` with parallel page scanning**
Use `concurrent.futures.ProcessPoolExecutor` or `ThreadPoolExecutor` for scanning pages concurrently, then group ranges and write output documents using `new_doc.insert_pdf(src_doc, from_page, to_page)`.
- [ ] **Step 3: Run pytest on splitter**
Run: `pytest tests/test_splitter.py -v`
Expected: PASS
- [ ] **Step 4: Commit splitter engine**

---

### Task 4: Modern Desktop GUI (`src/ui/app.py` & `main.py`)

**Files:**
- Create: `src/ui/app.py`
- Create: `main.py`

**Interfaces:**
- Consumes: `src/core/splitter.py`
- Produces: Desktop UI application window with async worker thread so UI remains responsive.

- [ ] **Step 1: Build the UI layout**
Add file selector / drag-drop area, output directory picker, separator text configuration (`DOCSEP`), mode selector (Discard / Preceding / Following), and naming pattern.
- [ ] **Step 2: Wire execution and real-time progress callbacks**
Connect Start button to background thread running `PdfSplitter.split()`, updating progress bar, status text, and split log.
- [ ] **Step 3: Add Open Output Folder and completion dialog**
- [ ] **Step 4: Test launching GUI locally**
Run: `python main.py --help` or test non-blocking GUI boot.
- [ ] **Step 5: Commit GUI application**

---

### Task 5: Packaging Standalone Windows `.exe`

**Files:**
- Create: `build_exe.py`
- Create: `PdfQRSplitter.spec`

- [ ] **Step 1: Write PyInstaller build script / spec**
Include hooks for `customtkinter`, `zxingcpp`, and `fitz` binaries.
- [ ] **Step 2: Build the standalone executable**
Run: `python build_exe.py` or `pyinstaller PdfQRSplitter.spec`
- [ ] **Step 3: Verify the executable output**
Verify `dist/PdfQRSplitter.exe` is generated and runs correctly.
- [ ] **Step 4: Document usage & Commit**
Create `README.md` with GUI guide and build instructions.
