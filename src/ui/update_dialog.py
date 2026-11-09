"""Update Available Dialog for Lumeed Psplit using CustomTkinter."""

import threading
import tkinter as tk
from typing import Optional
import customtkinter as ctk

from src.core.updater import UpdateDownloader, launch_installer_and_exit


class UpdateDialog(ctk.CTkToplevel):
    """Modal dialog notifying the user of an available update and providing one-click install."""

    def __init__(
        self, 
        parent, 
        new_version: str, 
        release_notes: str, 
        download_url: str,
        on_remind_later: Optional[callable] = None
    ):
        super().__init__(parent)
        self.parent = parent
        self.new_version = new_version
        self.release_notes = release_notes
        self.download_url = download_url
        self.on_remind_later = on_remind_later
        self.downloader: Optional[UpdateDownloader] = None
        self.is_downloading = False

        self.title("Update Available")
        self.geometry("540x440")
        self.minsize(480, 380)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Title
        title_label = ctk.CTkLabel(
            self,
            text=f"Lumeed Psplit {self.new_version} is available!",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, padx=25, pady=(20, 4), sticky="w")

        sub_label = ctk.CTkLabel(
            self,
            text="A new version is ready to install. Review the release notes below:",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        sub_label.grid(row=1, column=0, padx=25, pady=(0, 10), sticky="w")

        # Release notes text
        self.notes_box = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=12))
        self.notes_box.insert("1.0", self.release_notes or "Bug fixes, performance improvements, and new features.")
        self.notes_box.configure(state="disabled")
        self.notes_box.grid(row=2, column=0, padx=25, pady=5, sticky="nsew")

        # Progress bar (hidden initially)
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, padx=25, pady=(10, 5), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.grid(row=1, column=0, pady=(4, 0), sticky="w")

        # Hide progress frame initially
        self.progress_frame.grid_remove()

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=25, pady=(10, 20), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Remind Me Later",
            width=140,
            fg_color="gray40",
            hover_color="gray30",
            command=self._on_cancel
        )
        self.cancel_btn.pack(side="left")

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Now",
            width=140,
            font=ctk.CTkFont(weight="bold"),
            command=self._start_download
        )
        self.update_btn.pack(side="right")

    def _start_download(self):
        if self.is_downloading:
            return

        self.is_downloading = True
        self.update_btn.pack_forget()
        self.cancel_btn.configure(text="Cancel Download")
        self.progress_frame.grid()
        self.status_label.configure(text="Starting download...")

        self.downloader = UpdateDownloader(self.download_url, self.new_version)

        def _worker():
            self.downloader.download(
                progress_callback=lambda p, d, t: self.after(0, self._on_progress, p, d, t),
                finished_callback=lambda path: self.after(0, self._on_finished, path),
                failed_callback=lambda err: self.after(0, self._on_failed, err)
            )

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def _on_progress(self, percent: int, downloaded_mb: float, total_mb: float):
        self.progress_bar.set(percent / 100.0)
        if total_mb > 0:
            self.status_label.configure(text=f"Downloading... {downloaded_mb:.1f} MB / {total_mb:.1f} MB ({percent}%)")
        else:
            self.status_label.configure(text=f"Downloading... {downloaded_mb:.1f} MB")

    def _on_finished(self, installer_path: str):
        self.progress_bar.set(1.0)
        self.status_label.configure(text="Download complete! Launching installer and restarting...")
        self.cancel_btn.configure(state="disabled")

        # Launch installer and exit cleanly
        self.after(800, lambda: launch_installer_and_exit(installer_path))

    def _on_failed(self, error_msg: str):
        self.is_downloading = False
        self.status_label.configure(text=f"Download failed: {error_msg}")
        self.cancel_btn.configure(text="Close")
        self.update_btn.pack(side="right")
        self.update_btn.configure(text="Retry Update")

    def _on_cancel(self):
        if self.downloader:
            self.downloader.cancel()
        if self.on_remind_later:
            self.on_remind_later()
        self.destroy()
