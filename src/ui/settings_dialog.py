"""Non-modal Settings panel for Lumeed Psplit (theme: System / Dark / Light)."""

import json
from pathlib import Path

import customtkinter as ctk

CONFIG_FILE = Path.home() / ".lumeed_psplit_config.json"


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
            corner_radius=12,
            border_width=1,
            fg_color=("gray95", "gray17"),
            border_color=("gray80", "gray35"),
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
            font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="✕", width=26, height=26, corner_radius=6,
            fg_color="transparent", hover_color=("gray85", "gray28"),
            text_color=("gray30", "gray80"), command=self.close
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            self, text="Appearance", font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w", text_color=("gray30", "gray75")
        ).grid(row=1, column=0, padx=16, pady=(8, 4), sticky="w")

        current = self.config.get("appearance_mode", "System")
        self.theme_var = ctk.StringVar(value=current.capitalize())

        self.theme_switch = ctk.CTkSegmentedButton(
            self,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self._on_theme_changed,
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
