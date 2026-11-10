"""Non-modal Settings panel for Folio (theme: Light / Dark / System)."""

import json
from pathlib import Path

import customtkinter as ctk

CONFIG_FILE = Path.home() / ".folio_config.json"


def load_user_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_user_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


class SettingsPanel(ctk.CTkFrame):
    """Inline settings card. Never grabs input, so theme changes can't freeze the app."""

    def __init__(self, parent, on_close=None):
        super().__init__(
            parent,
            corner_radius=16,
            border_width=1,
            fg_color=("#FFFFFF", "#121A2C"),
            border_color=("#DCE8FA", "#1E2A42"),
        )
        self.parent = parent
        self._on_close = on_close
        self.config = load_user_config()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Settings",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="✕", width=22, height=22, corner_radius=11,
            fg_color="transparent", hover_color=("#EFEFEA", "#262A25"),
            text_color=("#82877C", "#949A8E"), command=self.close
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            self, text="Appearance", font=ctk.CTkFont(size=11),
            anchor="w", text_color=("#82877C", "#949A8E")
        ).grid(row=1, column=0, padx=16, pady=(6, 4), sticky="w")

        current = self.config.get("appearance_mode", "Light")
        self.theme_var = ctk.StringVar(value=current.capitalize())

        self.theme_switch = ctk.CTkSegmentedButton(
            self,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            command=self._on_theme_changed,
            selected_color="#1677FF",
            selected_hover_color="#0E5FD9",
            corner_radius=8,
        )
        self.theme_switch.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="ew")

    def _on_theme_changed(self, choice: str):
        ctk.set_appearance_mode(choice)
        self.config["appearance_mode"] = choice
        save_user_config(self.config)
        try:
            self.parent.update_idletasks()
        except Exception:
            pass

    def close(self):
        if callable(self._on_close):
            self._on_close()
