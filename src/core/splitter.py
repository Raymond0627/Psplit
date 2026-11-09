"""Lossless PDF Splitter and Parallel Orchestrator."""

import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, List, Optional
import fitz

from src.core.scanner import scan_page

@dataclass
class SplitResult:
    output_files: List[str] = field(default_factory=list)
    total_pages: int = 0
    splits_count: int = 0
    elapsed_seconds: float = 0.0
    separator_pages: List[int] = field(default_factory=list)

class PdfSplitter:
    """High-performance PDF splitter based on barcode separator sheets."""

    def __init__(self, dpi: int = 150):
        self.dpi = dpi

    def _matches_separator(
        self, 
        barcode_value: str, 
        separator_text: str, 
        match_type: str
    ) -> bool:
        """Check if barcode text matches separator criterion."""
        val = barcode_value.strip()
        sep = separator_text.strip()
        if not val or not sep:
            return False

        if match_type == "exact":
            return val.lower() == sep.lower()
        elif match_type == "regex":
            try:
                return bool(re.search(sep, val, re.IGNORECASE))
            except re.error:
                return False
        else:  # "contains" (default)
            return sep.lower() in val.lower()

    def split(
        self,
        pdf_path: str,
        output_dir: str,
        separator_text: str = "DOCSEP",
        mode: str = "discard",
        match_type: str = "contains",
        naming_pattern: str = "{original_name}_part_{index:03d}",
        max_workers: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> SplitResult:
        """Split a PDF into multiple documents using detected separator barcodes.
        
        Args:
            pdf_path: Path to the input PDF file.
            output_dir: Directory to save generated PDF files.
            separator_text: Barcode content to trigger document split.
            mode: 'discard', 'keep_prev', or 'keep_next'.
            match_type: 'contains', 'exact', or 'regex'.
            naming_pattern: Format string for output filenames.
            max_workers: Number of threads for parallel scanning.
            progress_callback: Callback func(completed_pages, total_pages, log_message).
        """
        start_time = time.time()
        os.makedirs(output_dir, exist_ok=True)

        src_doc = fitz.open(pdf_path)
        total_pages = len(src_doc)
        if total_pages == 0:
            src_doc.close()
            return SplitResult(total_pages=0, elapsed_seconds=0.0)

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 1. Parallel scanning of all pages
        page_results = {}
        completed_count = 0
        workers = max_workers or min(32, (os.cpu_count() or 4) * 2)

        def _scan_worker(p_idx):
            barcodes = scan_page(pdf_path, p_idx, dpi=self.dpi)
            return p_idx, barcodes

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_scan_worker, i) for i in range(total_pages)]
            for fut in as_completed(futures):
                p_idx, barcodes = fut.result()
                page_results[p_idx] = barcodes
                completed_count += 1
                if progress_callback:
                    progress_callback(
                        completed_count, 
                        total_pages, 
                        f"Scanned page {p_idx + 1}/{total_pages} ({len(barcodes)} barcodes found)"
                    )

        # 2. Identify separator pages
        separator_pages = set()
        for p_idx in range(total_pages):
            for bc in page_results.get(p_idx, []):
                if self._matches_separator(bc, separator_text, match_type):
                    separator_pages.add(p_idx)
                    break

        sorted_separators = sorted(list(separator_pages))

        # 3. Partition pages into document groups based on mode
        # Groups will be a list of lists of 0-based page indices: [[0, 1], [3], [5]]
        document_groups: List[List[int]] = []
        current_group: List[int] = []

        for p_idx in range(total_pages):
            is_sep = p_idx in separator_pages

            if is_sep:
                if mode == "keep_prev":
                    current_group.append(p_idx)
                    if current_group:
                        document_groups.append(current_group)
                        current_group = []
                elif mode == "keep_next":
                    if current_group:
                        document_groups.append(current_group)
                    current_group = [p_idx]
                else:  # "discard"
                    if current_group:
                        document_groups.append(current_group)
                        current_group = []
            else:
                current_group.append(p_idx)

        if current_group:
            document_groups.append(current_group)

        # Filter out empty groups (e.g. if separator was on page 0 with mode="discard")
        document_groups = [grp for grp in document_groups if grp]

        # If no documents generated (e.g., single page was a discarded separator)
        # or no separators at all, document_groups correctly has 0 or 1 doc.
        output_files: List[str] = []

        # 4. Lossless extraction of document groups
        for idx, page_indices in enumerate(document_groups, start=1):
            out_doc = fitz.open()
            for p_num in page_indices:
                out_doc.insert_pdf(src_doc, from_page=p_num, to_page=p_num)

            filename = naming_pattern.format(
                original_name=base_name,
                index=idx,
                total_splits=len(document_groups),
                start_page=page_indices[0] + 1,
                end_page=page_indices[-1] + 1,
            )
            if not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            out_filepath = os.path.join(output_dir, filename)
            out_doc.save(out_filepath)
            out_doc.close()
            output_files.append(out_filepath)

        src_doc.close()
        elapsed = time.time() - start_time

        return SplitResult(
            output_files=output_files,
            total_pages=total_pages,
            splits_count=len(output_files),
            elapsed_seconds=elapsed,
            separator_pages=sorted_separators,
        )
