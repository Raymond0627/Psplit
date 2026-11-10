"""Folio — Modern Minimalist PDF QR & Barcode Separator."""

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
from src.core.updater import check_github_update
from src.ui.update_dialog import UpdateDialog
from src.ui.settings_dialog import SettingsPanel, load_user_config
from src.ui.icons import (
    arrow_down_icon,
    gear_icon,
    logo_mark_icon,
    badge_icon,
    folder_icon,
    play_icon,
    info_icon,
    document_illustration,
)
from src.version import __version__

APP_TITLE = "Folio"

# ---- Design tokens matching the modern rounded-blue reference UI ----
PAD = 22
GAP = 12
RADIUS = 16          # Large soft rounded card corners
H_CONTROL = 36       # Pill inputs & option menus
H_BUTTON = 36        # Pill action buttons
H_ICON = 32          # Header round icon buttons

# Soft modern sky/blue palette
BG_LIGHT = "#EAF2FD"
BG_DARK = "#0B1220"
CARD_LIGHT = "#FFFFFF"
CARD_DARK = "#121A2C"
BORDER_LIGHT = "#DCE8FA"
BORDER_DARK = "#1E2A42"
INPUT_LIGHT = "#F4F7FC"
INPUT_DARK = "#172238"
INPUT_BORDER_LIGHT = "#D7E4F7"
INPUT_BORDER_DARK = "#263553"

PRIMARY_BLUE = "#1677FF"
PRIMARY_HOVER = "#0E5FD9"
MUTED_LABEL = ("#475569", "#94A3B8")

CARD_KW = dict(
    corner_radius=RADIUS,
    fg_color=(CARD_LIGHT, CARD_DARK),
    border_width=1,
    border_color=(BORDER_LIGHT, BORDER_DARK),
)

ctk.set_appearance_mode("Light")
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
        self.geometry("820x680")
        self.minsize(720, 600)
        self.configure(fg_color=(BG_LIGHT, BG_DARK))

        # Set window icon if available
        self._set_app_icon()

        # Load saved user theme preference (defaults to Light)
        config = load_user_config()
        saved_theme = config.get("appearance_mode", "Light")
        ctk.set_appearance_mode(saved_theme)

        self.splitter = PdfSplitter()
        self.is_processing = False
        self.last_output_dir = ""
        self.update_info = None  # (version_tag, release_notes, download_url)
        self.has_update = False
        self._settings_panel = None
        self._update_dialog = None
        self._log_visible = False

        self._build_ui()

        # Check for system updates in the background after 2 seconds
        self.after(2000, self._check_updates_background)

    def _set_app_icon(self):
        ico_path = get_resource_path("icon.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # -------------------------------------------------------------
        # 1. Header (Logo mark + App title + version + header controls)
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=PAD, pady=(PAD - 4, GAP), sticky="ew")

        # Left: "Folio" + version text (no logo mark)
        left_brand = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_brand.pack(side="left", anchor="w")

        ctk.CTkLabel(
            left_brand,
            text=APP_TITLE,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(side="left")

        ctk.CTkLabel(
            left_brand,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=11),
            text_color=MUTED_LABEL,
        ).pack(side="left", padx=(8, 0), pady=(2, 0))

        # Right: Minimize bar + Download Arrow + Gear Settings
        self._gear_img = ctk.CTkImage(
            light_image=gear_icon("#475569", 18),
            dark_image=gear_icon("#94A3B8", 18),
            size=(16, 16),
        )
        self._arrow_idle_img = ctk.CTkImage(
            light_image=arrow_down_icon("#475569", 18),
            dark_image=arrow_down_icon("#94A3B8", 18),
            size=(16, 16),
        )
        self._arrow_active_img = ctk.CTkImage(
            light_image=arrow_down_icon("#FFFFFF", 18),
            dark_image=arrow_down_icon("#FFFFFF", 18),
            size=(16, 16),
        )

        self.header_settings_btn = ctk.CTkButton(
            header_frame,
            text="",
            image=self._gear_img,
            width=H_ICON,
            height=H_ICON,
            corner_radius=H_ICON // 2,
            fg_color="transparent",
            hover_color=("#DCE8FA", "#1E2A42"),
            command=self._toggle_settings_panel,
        )
        self.header_settings_btn.pack(side="right")

        self.header_update_btn = ctk.CTkButton(
            header_frame,
            text="",
            image=self._arrow_idle_img,
            width=H_ICON,
            height=H_ICON,
            corner_radius=H_ICON // 2,
            fg_color="transparent",
            hover_color=("#DCE8FA", "#1E2A42"),
            command=self._on_click_update_btn,
        )
        self.header_update_btn.pack(side="right", padx=(0, 4))

        # -------------------------------------------------------------
        # 2. Card 1: Input / Output Folders
        # -------------------------------------------------------------
        io_frame = ctk.CTkFrame(self, **CARD_KW)
        io_frame.grid(row=1, column=0, padx=PAD, pady=(0, GAP), sticky="ew")
        io_frame.grid_columnconfigure(0, weight=1)

        # Header of Card 1: Blue badge + "Input PDF"
        io_head = ctk.CTkFrame(io_frame, fg_color="transparent")
        io_head.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 8), sticky="w")

        self._doc_badge_img = ctk.CTkImage(
            light_image=badge_icon("document", PRIMARY_BLUE, 20),
            dark_image=badge_icon("document", PRIMARY_BLUE, 20),
            size=(20, 20),
        )
        ctk.CTkLabel(io_head, text="", image=self._doc_badge_img).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            io_head,
            text="Input PDF",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(side="left")

        # Row 1: Input PDF entry + Pill Browse button
        r1 = ctk.CTkFrame(io_frame, fg_color="transparent")
        r1.grid(row=1, column=0, columnspan=2, padx=18, pady=(0, 10), sticky="ew")
        r1.grid_columnconfigure(0, weight=1)

        self.pdf_entry = ctk.CTkEntry(
            r1,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            border_width=1,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            border_color=(INPUT_BORDER_LIGHT, INPUT_BORDER_DARK),
            text_color=("#0F172A", "#F8FAFC"),
            placeholder_text="",
        )
        self.pdf_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self._folder_white_img = ctk.CTkImage(
            light_image=folder_icon("#FFFFFF", 14),
            dark_image=folder_icon("#FFFFFF", 14),
            size=(14, 14),
        )
        browse_pdf_btn = ctk.CTkButton(
            r1,
            text="Browse",
            image=self._folder_white_img,
            compound="left",
            width=96,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_HOVER,
            text_color="#FFFFFF",
            command=self._browse_pdf,
        )
        browse_pdf_btn.grid(row=0, column=1, sticky="e")

        # Output folders sub-label
        r2_label = ctk.CTkFrame(io_frame, fg_color="transparent")
        r2_label.grid(row=2, column=0, columnspan=2, padx=18, pady=(2, 4), sticky="w")
        ctk.CTkLabel(
            r2_label,
            text="⚙ Output folders",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MUTED_LABEL,
        ).pack(side="left")

        # Row 2: Output folder entry + Pill Choose button
        r2 = ctk.CTkFrame(io_frame, fg_color="transparent")
        r2.grid(row=3, column=0, columnspan=2, padx=18, pady=(0, 16), sticky="ew")
        r2.grid_columnconfigure(0, weight=1)

        self.out_entry = ctk.CTkEntry(
            r2,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            border_width=1,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            border_color=(INPUT_BORDER_LIGHT, INPUT_BORDER_DARK),
            text_color=("#0F172A", "#F8FAFC"),
            placeholder_text="(Defaults to output/ next to the PDF...)",
            placeholder_text_color=MUTED_LABEL,
        )
        self.out_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self._folder_blue_img = ctk.CTkImage(
            light_image=folder_icon(PRIMARY_BLUE, 14),
            dark_image=folder_icon(PRIMARY_BLUE, 14),
            size=(14, 14),
        )
        browse_out_btn = ctk.CTkButton(
            r2,
            text="Choose",
            image=self._folder_blue_img,
            compound="left",
            width=96,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#EDF4FF", "#18233A"),
            hover_color=("#DCE8FA", "#1E2C48"),
            text_color=PRIMARY_BLUE,
            command=self._browse_output,
        )
        browse_out_btn.grid(row=0, column=1, sticky="e")

        # -------------------------------------------------------------
        # 3. Card 2: Split Rules
        # -------------------------------------------------------------
        opts_frame = ctk.CTkFrame(self, **CARD_KW)
        opts_frame.grid(row=2, column=0, padx=PAD, pady=(0, GAP), sticky="ew")
        opts_frame.grid_columnconfigure(0, weight=1)
        opts_frame.grid_columnconfigure(1, weight=1)

        # Header of Card 2: Lightning badge + "Split Rules" + info icon
        opts_head = ctk.CTkFrame(opts_frame, fg_color="transparent")
        opts_head.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 8), sticky="ew")

        left_opts_head = ctk.CTkFrame(opts_head, fg_color="transparent")
        left_opts_head.pack(side="left", anchor="w")

        self._bolt_badge_img = ctk.CTkImage(
            light_image=badge_icon("lightning", PRIMARY_BLUE, 20),
            dark_image=badge_icon("lightning", PRIMARY_BLUE, 20),
            size=(20, 20),
        )
        ctk.CTkLabel(left_opts_head, text="", image=self._bolt_badge_img).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            left_opts_head,
            text="Split Rules",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(side="left")

        self._info_img = ctk.CTkImage(
            light_image=info_icon("#64748B", 18),
            dark_image=info_icon("#94A3B8", 18),
            size=(16, 16),
        )
        ctk.CTkLabel(opts_head, text="", image=self._info_img).pack(side="right")

        # Left col: Separator text | Right col: Match type
        ctk.CTkLabel(
            opts_frame,
            text="Separator text",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).grid(row=1, column=0, padx=(18, 10), pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            opts_frame,
            text="Match type",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).grid(row=1, column=1, padx=(10, 18), pady=(0, 4), sticky="w")

        self.sep_entry = ctk.CTkEntry(
            opts_frame,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            border_width=1,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            border_color=(INPUT_BORDER_LIGHT, INPUT_BORDER_DARK),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.sep_entry.insert(0, "DOCSEP")
        self.sep_entry.grid(row=2, column=0, padx=(18, 10), pady=(0, 10), sticky="ew")

        self.match_type_var = ctk.StringVar(value="contains")
        match_menu = ctk.CTkOptionMenu(
            opts_frame,
            values=["contains", "exact", "regex"],
            variable=self.match_type_var,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            button_color=(INPUT_LIGHT, INPUT_DARK),
            button_hover_color=("#E5EDF9", "#1C2A44"),
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=(CARD_LIGHT, CARD_DARK),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
        )
        match_menu.grid(row=2, column=1, padx=(10, 18), pady=(0, 10), sticky="ew")

        # Left col: Separator page | Right col: Filename pattern
        ctk.CTkLabel(
            opts_frame,
            text="Separator page",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).grid(row=3, column=0, padx=(18, 10), pady=(0, 4), sticky="w")

        ctk.CTkLabel(
            opts_frame,
            text="Filename pattern",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).grid(row=3, column=1, padx=(10, 18), pady=(0, 4), sticky="w")

        self.mode_var = ctk.StringVar(value="discard")
        mode_menu = ctk.CTkOptionMenu(
            opts_frame,
            values=["Discard", "Keep previous", "Keep next"],
            command=self._on_mode_change,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            button_color=(INPUT_LIGHT, INPUT_DARK),
            button_hover_color=("#E5EDF9", "#1C2A44"),
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=(CARD_LIGHT, CARD_DARK),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
        )
        mode_menu.grid(row=4, column=0, padx=(18, 10), pady=(0, 16), sticky="ew")

        self.pattern_entry = ctk.CTkEntry(
            opts_frame,
            height=H_CONTROL,
            corner_radius=H_CONTROL // 2,
            border_width=1,
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            border_color=(INPUT_BORDER_LIGHT, INPUT_BORDER_DARK),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.pattern_entry.insert(0, "{original_name}_part_{index:03d}")
        self.pattern_entry.grid(row=4, column=1, padx=(10, 18), pady=(0, 16), sticky="ew")

        # -------------------------------------------------------------
        # 4. Card 3: Ready / Activity state with illustration
        # -------------------------------------------------------------
        exec_frame = ctk.CTkFrame(self, **CARD_KW)
        exec_frame.grid(row=3, column=0, padx=PAD, pady=(0, GAP), sticky="nsew")
        exec_frame.grid_rowconfigure(1, weight=1)
        exec_frame.grid_columnconfigure(0, weight=1)

        # Header of Card 3: List badge + "Ready" + Status pill
        exec_head = ctk.CTkFrame(exec_frame, fg_color="transparent")
        exec_head.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="ew")

        left_exec_head = ctk.CTkFrame(exec_head, fg_color="transparent")
        left_exec_head.pack(side="left", anchor="w")

        self._list_badge_img = ctk.CTkImage(
            light_image=badge_icon("list", PRIMARY_BLUE, 20),
            dark_image=badge_icon("list", PRIMARY_BLUE, 20),
            size=(20, 20),
        )
        ctk.CTkLabel(left_exec_head, text="", image=self._list_badge_img).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            left_exec_head,
            text="Ready",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(side="left")

        # Right side status indicator: green dot + "Ready"
        status_box = ctk.CTkFrame(exec_head, fg_color="transparent")
        status_box.pack(side="right")
        self.status_dot = ctk.CTkLabel(
            status_box,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color="#10B981",
        )
        self.status_dot.pack(side="left", padx=(0, 4))
        self.progress_label = ctk.CTkLabel(
            status_box,
            text="Ready",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.progress_label.pack(side="left")

        # Subtle progress bar track across card
        self.progress_bar = ctk.CTkProgressBar(
            exec_frame,
            height=4,
            corner_radius=2,
            fg_color=(BORDER_LIGHT, BORDER_DARK),
            progress_color=PRIMARY_BLUE,
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, padx=18, pady=(0, 4), sticky="new")

        # Central container: shows cute illustration empty state by default, swaps to log when splitting
        self.center_container = ctk.CTkFrame(exec_frame, fg_color="transparent")
        self.center_container.grid(row=2, column=0, padx=18, pady=(4, 16), sticky="nsew")
        self.center_container.grid_rowconfigure(0, weight=1)
        self.center_container.grid_columnconfigure(0, weight=1)
        exec_frame.grid_rowconfigure(2, weight=1)

        # Empty state view matching reference: document illustration + subtitle
        self.empty_view = ctk.CTkFrame(self.center_container, fg_color="transparent")
        self.empty_view.grid(row=0, column=0, sticky="nsew")

        self._doc_illus_img = ctk.CTkImage(
            light_image=document_illustration(180, 115),
            dark_image=document_illustration(180, 115),
            size=(180, 115),
        )
        ctk.CTkLabel(self.empty_view, text="", image=self._doc_illus_img).pack(expand=True, pady=(10, 4))
        ctk.CTkLabel(
            self.empty_view,
            text="Configure your settings and click Start splitting",
            font=ctk.CTkFont(size=12),
            text_color=MUTED_LABEL,
        ).pack(pady=(0, 12))

        # Log box view (initially hidden, revealed on split start)
        self.log_box = ctk.CTkTextbox(
            self.center_container,
            wrap="word",
            corner_radius=10,
            border_width=1,
            border_color=(BORDER_LIGHT, BORDER_DARK),
            fg_color=(INPUT_LIGHT, INPUT_DARK),
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=("#0F172A", "#F8FAFC"),
        )

        # -------------------------------------------------------------
        # 5. Bottom Action Bar: Pill "Open folder" & "Start splitting"
        # -------------------------------------------------------------
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.grid(row=4, column=0, padx=PAD, pady=(0, PAD), sticky="ew")

        self.open_btn = ctk.CTkButton(
            action_bar,
            text="Open folder",
            image=self._folder_blue_img,
            compound="left",
            width=124,
            height=H_BUTTON,
            corner_radius=H_BUTTON // 2,
            fg_color=CARD_LIGHT,
            border_width=1,
            border_color=PRIMARY_BLUE,
            hover_color=("#EDF4FF", "#18233A"),
            text_color=PRIMARY_BLUE,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled",
            command=self._open_output_folder,
        )
        self.open_btn.pack(side="left")

        self._play_img = ctk.CTkImage(
            light_image=play_icon("#FFFFFF", 12),
            dark_image=play_icon("#FFFFFF", 12),
            size=(12, 12),
        )
        self.start_btn = ctk.CTkButton(
            action_bar,
            text="Start splitting",
            image=self._play_img,
            compound="left",
            height=H_BUTTON,
            width=138,
            corner_radius=H_BUTTON // 2,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_HOVER,
            text_color="#FFFFFF",
            command=self._start_split_thread,
        )
        self.start_btn.pack(side="right")

    def _on_mode_change(self, choice: str):
        mapping = {
            "Discard": "discard",
            "Keep previous": "keep_prev",
            "Keep next": "keep_next",
        }
        self.mode_var.set(mapping.get(choice, "discard"))

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

    def _show_log_view(self):
        if not self._log_visible:
            self.empty_view.grid_forget()
            self.log_box.grid(row=0, column=0, sticky="nsew")
            self._log_visible = True

    def _log(self, message: str):
        self._show_log_view()
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
        self.open_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_dot.configure(text_color="#F59E0B")
        self.progress_label.configure(text="Processing...")

        self._show_log_view()
        self.log_box.delete("1.0", tk.END)
        self._log(f"Starting split: {os.path.basename(pdf_path)}")
        self._log(f"Separator: '{separator_text}' ({match_type}, {mode})\n")

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
        self.progress_label.configure(text=f"{int(fraction * 100)}%")
        self._log(f"  -> {msg}")

    def _on_complete(self, result: SplitResult, output_dir: str):
        self.is_processing = False
        self.start_btn.configure(state="normal")
        self.last_output_dir = output_dir
        self.open_btn.configure(state="normal")
        self.status_dot.configure(text_color="#10B981")
        self.progress_label.configure(text="Complete")
        self.progress_bar.set(1.0)

        self._log("\n" + "=" * 50)
        self._log(f"SUCCESS: Split into {result.splits_count} documents in {result.elapsed_seconds:.2f}s.")
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
        self.status_dot.configure(text_color="#EF4444")
        self.progress_label.configure(text="Failed")
        self._log(f"\nERROR: {err_msg}")
        messagebox.showerror("Splitting Failed", f"An error occurred:\n{err_msg}")

    # ================= Update Handling =================
    def _check_updates_background(self):
        def _worker():
            res = check_github_update()
            if res:
                tag, notes, url = res
                self.after(0, self._on_update_found, tag, notes, url)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_update_found(self, tag: str, notes: str, url: str):
        self.update_info = (tag, notes, url)
        self.has_update = True
        self.header_update_btn.configure(
            text=f" {tag}",
            image=self._arrow_active_img,
            width=88,
            corner_radius=H_ICON // 2,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_HOVER,
            text_color="#FFFFFF",
        )
        self._show_update_dialog()

    def _show_update_dialog(self):
        if not self.update_info:
            return
        if self._update_dialog is not None and self._update_dialog.winfo_exists():
            self._update_dialog.lift()
            self._update_dialog.focus_force()
            return
        tag, notes, url = self.update_info
        dlg = UpdateDialog(
            parent=self,
            new_version=tag,
            release_notes=notes,
            download_url=url,
            on_remind_later=self._on_remind_later,
        )
        dlg.on_close_callback = self._on_update_dialog_closed
        self._update_dialog = dlg

    def _on_update_dialog_closed(self):
        self._update_dialog = None

    def _on_remind_later(self):
        pass

    def _on_click_update_btn(self):
        if self.has_update and self.update_info:
            self._show_update_dialog()
        else:
            messagebox.showinfo(APP_TITLE, f"You are on the latest version ({__version__}).")

    # ================= Settings Handling (inline, non-modal) =================
    def _toggle_settings_panel(self):
        if self._settings_panel is None:
            self._settings_panel = SettingsPanel(self, on_close=self._on_close_settings_panel)
            self._settings_panel.place(relx=1.0, rely=0.0, x=-PAD, y=56, anchor="ne")
            self._settings_panel.lift()
        elif self._settings_panel.winfo_manager() == "place":
            self._on_close_settings_panel()
        else:
            self._settings_panel.place(relx=1.0, rely=0.0, x=-PAD, y=56, anchor="ne")
            self._settings_panel.lift()

    def _on_close_settings_panel(self):
        if self._settings_panel is not None:
            self._settings_panel.place_forget()

    def _open_settings_dialog(self):
        self._toggle_settings_panel()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
