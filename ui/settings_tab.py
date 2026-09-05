import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Callable

from config.settings import settings
from ui.directory_entry import DirectoryEntry


class SettingsTab(tk.Frame):
    """Settings tab for the application."""
    
    def __init__(self, parent, on_apply: Callable[[], None] | None = None):
        super().__init__(parent)
        self._on_settings_applied = on_apply
        self._create_form()
        self._create_apply_button()

    def _create_form(self) -> None:
        form_frame = tk.Frame(self)
        form_frame.pack(side="top", fill="x", padx=10, pady=10)

        tk.Label(form_frame, text="Path to game saves:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.entry_game_saves = DirectoryEntry(
            form_frame,
            initial_value=settings.GAME_SAVE_DIR,
        )
        self.entry_game_saves.grid(
            row=0, column=1, sticky="ew", padx=(10, 0), pady=5
        )

        tk.Label(form_frame, text="Path to common storage:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.entry_common_storage = DirectoryEntry(
            form_frame,
            initial_value=settings.SAVES_DIR,
        )
        self.entry_common_storage.grid(
            row=1, column=1, sticky="ew", padx=(10, 0), pady=5
        )

        form_frame.columnconfigure(1, weight=1)

    def _create_apply_button(self) -> None:
        tk.Button(
            self, text="Apply", command=self._on_apply, width=10
        ).pack(side="bottom", anchor="e", padx=5, pady=5)

    def _on_apply(self) -> None:
        game_save_dir = self.entry_game_saves.get().strip()
        saves_dir = self.entry_common_storage.get().strip()

        if not game_save_dir or not saves_dir:
            messagebox.showerror(
                "Invalid settings",
                "Directory paths cannot be empty.",
                parent=self,
            )
            return

        settings.GAME_SAVE_DIR = Path(game_save_dir)
        settings.SAVES_DIR = Path(saves_dir)
        settings.export()

        if self._on_settings_applied is not None:
            self._on_settings_applied()

        messagebox.showinfo(
            "Settings",
            "Settings saved.",
            parent=self,
        )
