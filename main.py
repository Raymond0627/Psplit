"""PDF QR & Barcode Splitter Entry Point."""

import argparse
import sys
import os

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.splitter import PdfSplitter

def run_cli(args):
    print(f"Processing PDF: {args.input}")
    print(f"Separator: '{args.separator}' (mode: {args.mode}, match: {args.match})")
    
    splitter = PdfSplitter(dpi=args.dpi)
    
    def cli_progress(completed, total, msg):
        pct = int(completed / total * 100) if total > 0 else 100
        print(f"[{pct:3d}%] {msg}")

    result = splitter.split(
        pdf_path=args.input,
        output_dir=args.output,
        separator_text=args.separator,
        mode=args.mode,
        match_type=args.match,
        naming_pattern=args.pattern,
        progress_callback=cli_progress if not args.quiet else None
    )

    print(f"\nDone! Split into {result.splits_count} files in {result.elapsed_seconds:.2f} seconds.")
    for f in result.output_files:
        print(f"  - {f}")

def main():
    parser = argparse.ArgumentParser(
        description="Lumeed QSplit - Super-optimized PDF QR & Barcode Splitter"
    )
    parser.add_argument("input", nargs="?", default=None, help="Input PDF file path (launches GUI if omitted)")
    parser.add_argument("-o", "--output", default="split_output", help="Output directory")
    parser.add_argument("-s", "--separator", default="DOCSEP", help="Separator text (default: DOCSEP)")
    parser.add_argument(
        "-m", "--mode", 
        choices=["discard", "keep_prev", "keep_next"], 
        default="discard",
        help="Separator page behavior: discard (default), keep_prev, or keep_next"
    )
    parser.add_argument(
        "--match", 
        choices=["contains", "exact", "regex"], 
        default="contains",
        help="Matching rule for separator (default: contains)"
    )
    parser.add_argument(
        "--pattern", 
        default="{original_name}_part_{index:03d}",
        help="Filename pattern (default: {original_name}_part_{index:03d})"
    )
    parser.add_argument("--dpi", type=int, default=150, help="Rendering DPI for barcode scan (default: 150)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (CLI)")

    args = parser.parse_args()

    if args.input:
        run_cli(args)
    else:
        # Launch modern GUI
        from src.ui.app import main as launch_gui
        launch_gui()

if __name__ == "__main__":
    main()
