# High-Performance PDF QR/Barcode Splitter Specification

**Date:** 2026-11-04  
**Project:** PDF QR Splitter Desktop (Local Executable)

---

## 1. Executive Summary
This project provides a modern, super-optimized desktop application and Windows standalone executable (`.exe`) to split large multi-page scanned PDF documents based on separator pages containing Barcodes or QR Codes (such as separator sheets with `DOCSEP`, custom QR codes, Code 128, Code 39, etc.).

It solves the critical flaws of the original `PdfQRSplit` tool:
- Eliminates temporary disk file churn by decoding barcodes directly in memory.
- Uses C/C++ native bindings (`PyMuPDF` for PDF rendering/splitting and `zxing-cpp` for barcode/QR decoding).
- Employs multi-threaded parallel page scanning across available CPU cores.
- Preserves full vector/scan quality and metadata using zero-loss PDF object extraction.
- Provides a clean, modern GUI with drag-and-drop support, customizable separator criteria, progress tracking, and standalone distribution via PyInstaller.

---

## 2. Architecture & Components

```
+-------------------------------------------------------+
|                    Desktop GUI                        |
|  (Tkinter / CustomTkinter with Drag & Drop & Theme)   |
+---------------------------+---------------------------+
                            | (Starts Worker Thread)
                            v
+-------------------------------------------------------+
|                Splitter Orchestrator                  |
|  (Manages PDF I/O, Worker Pool, Progress & Callback)  |
+---------------------------+---------------------------+
                            |
           +----------------+----------------+
           |                                 |
           v                                 v
+-----------------------+         +---------------------+
|   Page Scan Engine    |         |   Lossless Splitter |
|  - PyMuPDF Pixmap     |         |  - PyMuPDF Range    |
|  - zxing-cpp Barcodes |         |    Extraction       |
|  - Multi-Core Workers |         |  - Custom Naming    |
+-----------------------+         +---------------------+
```

### 2.1 Core Modules
1. **`core/scanner.py`**:
   - Analyzes individual PDF pages.
   - Extracts page image directly or renders at 150 DPI in memory.
   - Invokes `zxingcpp.read_barcodes` against raw memory buffer.
   - Returns list of detected barcodes and text contents.
2. **`core/splitter.py`**:
   - Inspects the full PDF, runs parallel page scanning across CPU workers.
   - Identifies separator pages matching the user's separator criteria (exact match, contains, regex).
   - Generates document segments according to separator policy:
     - `discard`: Separator page is omitted.
     - `keep_prev`: Separator page is attached to the preceding document.
     - `keep_next`: Separator page is attached to the following document.
   - Performs lossless sub-document extraction via `doc.insert_pdf(...)` without raster recompression.
   - Supports naming templates (e.g. `{original_name}_part_{index:03d}.pdf` or barcode text).
3. **`ui/app.py`**:
   - Modern UI window.
   - Drag & drop PDF file zone.
   - Input fields: Separator string/pattern, separator handling mode, output folder, prefix/template.
   - Execution controls, real-time progress bar, live event logging, and output folder opener.
4. **`packaging/`**:
   - `build_exe.py` and PyInstaller configuration specification.
   - Bundles all native DLLs (MuPDF, zxing-cpp runtime) into a standalone `.exe`.

---

## 3. Technology Choices
- **Language / Runtime:** Python 3.10+
- **PDF Engine:** `PyMuPDF` (`fitz` >= 1.23.0) — C-based, fastest PDF engine available.
- **Barcode & QR Engine:** `zxing-cpp` (>= 2.2.0) — C++ implementation of ZXing, parses directly from raw RGB/Grayscale numpy arrays or bytes.
- **GUI Framework:** `customtkinter` (or modern Tkinter with ttk themes) + `tkinterdnd2` for native Windows drag-and-drop.
- **Packaging:** `pyinstaller` to create single executable or portable folder distribution.

---

## 4. Verification & Testing Strategy
- Unit tests with generated test PDFs containing QR codes and Code 128 barcodes.
- Tests covering all separator modes (`discard`, `keep_prev`, `keep_next`).
- Tests verifying multi-core parallel performance and memory stability.
- Build verification ensuring the `.exe` packages and launches cleanly.
