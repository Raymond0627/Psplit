"""Modern Desktop GUI for PDF QR/Barcode Splitter using CustomTkinter."""

import os
import sys
import subprocess
import threading
from typing import Optional
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

from src.core.splitter import PdfSplitter, SplitResult

APP_TITLE = "Lumeed Psplit"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("820x720")
        self.minsize(700, 600)

        # Set window icon if available
        self._set_app_icon()

        self.splitter = PdfSplitter()
        self.is_processing = False
        self.last_output_dir = ""

        self._build_ui()

    def _set_app_icon(self):
        ico_path = get_resource_path("icon.ico")
        png_path = get_resource_path("icon.png")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass
        if os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.iconphoto(False, img)
            except Exception:
                pass

    def _build_ui(self):
        # Configure layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header Title Banner
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        # Load small logo icon into banner if icon.png exists
        png_path = get_resource_path("icon.png")
        if os.path.exists(png_path):
            try:
                logo_pil = Image.open(png_path).resize((36, 36))
                self.header_logo = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(36, 36))
                logo_label = ctk.CTkLabel(header_frame, image=self.header_logo, text="")
                logo_label.pack(side="left", padx=(15, 5), pady=10)
            except Exception:
                pass
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text=APP_TITLE, 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=(10, 5), pady=10)

        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="High-Speed In-Memory Splitting (QR & Barcodes)", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack(side="left", padx=5, pady=10)

        # File & Folder Selection Frame
        io_frame = ctk.CTkFrame(self, corner_radius=10)
        io_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        io_frame.grid_columnconfigure(1, weight=1)

        # Input PDF
        ctk.CTkLabel(io_frame, text="Input PDF:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=15, pady=(12, 6), sticky="w"
        )
        self.pdf_entry = ctk.CTkEntry(io_frame, placeholder_text="Select a multi-page PDF file...")
        self.pdf_entry.grid(row=0, column=1, padx=10, pady=(12, 6), sticky="ew")
        browse_pdf_btn = ctk.CTkButton(io_frame, text="Browse File", width=110, command=self._browse_pdf)
        browse_pdf_btn.grid(row=0, column=2, padx=15, pady=(12, 6))

        # Output Folder
        ctk.CTkLabel(io_frame, text="Output Folder:", font=ctk.CTkFont(weight="bold")).grid(
            row=1, column=0, padx=15, pady=(6, 12), sticky="w"
        )
        self.out_entry = ctk.CTkEntry(io_frame, placeholder_text="Defaults to output/ next to PDF...")
        self.out_entry.grid(row=1, column=1, padx=10, pady=(6, 12), sticky="ew")
        browse_out_btn = ctk.CTkButton(io_frame, text="Browse Folder", width=110, command=self._browse_output)
        browse_out_btn.grid(row=1, column=2, padx=15, pady=(6, 12))

        # Configuration Options Frame
        opts_frame = ctk.CTkFrame(self, corner_radius=10)
        opts_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        opts_frame.grid_columnconfigure(1, weight=1)
        opts_frame.grid_columnconfigure(3, weight=1)

        # Separator string
        ctk.CTkLabel(opts_frame, text="Separator Text:").grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.sep_entry = ctk.CTkEntry(opts_frame)
        self.sep_entry.insert(0, "DOCSEP")
        self.sep_entry.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ew")

        # Match Type
        ctk.CTkLabel(opts_frame, text="Match Type:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.match_type_var = ctk.StringVar(value="contains")
        match_menu = ctk.CTkOptionMenu(
            opts_frame, 
            values=["contains", "exact", "regex"],
            variable=self.match_type_var,
            width=120
        )
        match_menu.grid(row=0, column=3, padx=(0, 15), pady=10, sticky="ew")

        # Separator page handling
        ctk.CTkLabel(opts_frame, text="Separator Page:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.mode_var = ctk.StringVar(value="discard")
        mode_menu = ctk.CTkOptionMenu(
            opts_frame,
            values=["discard (Remove separator)", "keep_prev (Keep with previous doc)", "keep_next (Keep with next doc)"],
            command=self._on_mode_change,
            width=220
        )
        mode_menu.grid(row=1, column=1, padx=(0, 15), pady=10, sticky="ew")

        # Naming Pattern
        ctk.CTkLabel(opts_frame, text="Naming Pattern:").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.pattern_entry = ctk.CTkEntry(opts_frame)
        self.pattern_entry.insert(0, "{original_name}_part_{index:03d}")
        self.pattern_entry.grid(row=1, column=3, padx=(0, 15), pady=10, sticky="ew")

        # Execution and Progress Area
        exec_frame = ctk.CTkFrame(self, corner_radius=10)
        exec_frame.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")
        exec_frame.grid_rowconfigure(2, weight=1)
        exec_frame.grid_columnconfigure(0, weight=1)

        # Progress bar & label
        prog_subframe = ctk.CTkFrame(exec_frame, fg_color="transparent")
        prog_subframe.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
        prog_subframe.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(prog_subframe)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.progress_label = ctk.CTkLabel(prog_subframe, text="Ready", width=120, anchor="e")
        self.progress_label.grid(row=0, column=1, sticky="e")

        # Log Text Box
        self.log_box = ctk.CTkTextbox(exec_frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")

        # Bottom Action Bar
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=4, column=0, padx=20, pady=(5, 15), sticky="ew")
        action_bar.grid_columnconfigure(0, weight=1)

        self.open_btn = ctk.CTkButton(
            action_bar, 
            text="Open Output Folder", 
            width=160, 
            state="disabled", 
            fg_color="gray40",
            command=self._open_output_folder
        )
        self.open_btn.pack(side="left", padx=5)

        self.start_btn = ctk.CTkButton(
            action_bar, 
            text="Start Splitting", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            width=180,
            command=self._start_split_thread
        )
        self.start_btn.pack(side="right", padx=5)

    def _on_mode_change(self, choice: str):
        if "discard" in choice:
            self.mode_var.set("discard")
        elif "keep_prev" in choice:
            self.mode_var.set("keep_prev")
        elif "keep_next" in choice:
            self.mode_var.set("keep_next")

    def _browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select PDF Document",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if filename:
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, filename)
            if not self.out_entry.get().strip():
                default_out = os.path.join(os.path.dirname(filename), "split_output")
                self.out_entry.delete(0, tk.END)
                self.out_entry.insert(0, default_out)

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, folder)

    def _log(self, message: str):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def _open_output_folder(self):
        if self.last_output_dir and os.path.exists(self.last_output_dir):
            if os.name == 'nt':
                os.startfile(self.last_output_dir)
            else:
                subprocess.Popen(["xdg-open", self.last_output_dir])

    def _start_split_thread(self):
        if self.is_processing:
            return

        pdf_path = self.pdf_entry.get().strip()
        if not pdf_path or not os.path.isfile(pdf_path):
            messagebox.showerror("Error", "Please select a valid input PDF file.")
            return

        output_dir = self.out_entry.get().strip()
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(pdf_path), "split_output")

        separator_text = self.sep_entry.get().strip()
        if not separator_text:
            messagebox.showerror("Error", "Separator text cannot be empty.")
            return

        mode = self.mode_var.get()
        match_type = self.match_type_var.get()
        naming_pattern = self.pattern_entry.get().strip() or "{original_name}_part_{index:03d}"

        self.is_processing = True
        self.start_btn.configure(state="disabled")
        self.open_btn.configure(state="disabled", fg_color="gray40")
        self.progress_bar.set(0)
        self.log_box.delete("1.0", tk.END)
        self._log(f"Starting split on: {os.path.basename(pdf_path)}")
        self._log(f"Separator: '{separator_text}' (match: {match_type}, mode: {mode})")
        self._log(f"Destination: {output_dir}\n")

        thread = threading.Thread(
            target=self._run_split,
            args=(pdf_path, output_dir, separator_text, mode, match_type, naming_pattern),
            daemon=True
        )
        thread.start()

    def _run_split(self, pdf_path, output_dir, separator_text, mode, match_type, naming_pattern):
        def _progress(completed, total, msg):
            self.after(0, self._update_progress, completed, total, msg)

        try:
            result = self.splitter.split(
                pdf_path=pdf_path,
                output_dir=output_dir,
                separator_text=separator_text,
                mode=mode,
                match_type=match_type,
                naming_pattern=naming_pattern,
                progress_callback=_progress
            )
            self.after(0, self._on_complete, result, output_dir)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _update_progress(self, completed: int, total: int, msg: str):
        fraction = completed / total if total > 0 else 0
        self.progress_bar.set(fraction)
        self.progress_label.configure(text=f"{completed}/{total} ({int(fraction * 100)}%)")
        self._log(f"  -> {msg}")

    def _on_complete(self, result: SplitResult, output_dir: str):
        self.is_processing = False
        self.start_btn.configure(state="normal")
        self.last_output_dir = output_dir
        self.open_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
        self.progress_label.configure(text="Finished")
        self.progress_bar.set(1.0)

        self._log("\n" + "=" * 50)
        self._log(f"SUCCESS: Split into {result.splits_count} documents in {result.elapsed_seconds:.2f} seconds.")
        if result.separator_pages:
            sep_pages_str = ", ".join(str(p + 1) for p in result.separator_pages)
            self._log(f"Separators detected on page(s): {sep_pages_str}")
        self._log("=" * 50 + "\n")

        for f in result.output_files:
            self._log(f"  Created: {os.path.basename(f)}")

        messagebox.showinfo(
            "Splitting Complete",
            f"Successfully created {result.splits_count} files in {result.elapsed_seconds:.2f}s!"
        )

    def _on_error(self, err_msg: str):
        self.is_processing = False
        self.start_btn.configure(state="normal")
        self.progress_label.configure(text="Failed")
        self._log(f"\nERROR: {err_msg}")
        messagebox.showerror("Splitting Failed", f"An error occurred:\n{err_msg}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
