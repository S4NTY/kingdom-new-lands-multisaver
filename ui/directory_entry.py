import tkinter as tk
from tkinter import filedialog
from pathlib import Path


class DirectoryEntry(tk.Frame):
    """Directory entry widget with a button to select a directory."""
    
    def __init__(self, parent, initial_value: str):
        super().__init__(parent)
        self.variable = tk.StringVar(self, value=initial_value)

        self.entry = tk.Entry(
            self,
            textvariable=self.variable,
            font="TkDefaultFont",
        )
        self.entry.pack(
            side="left", fill="x", expand=True
        )
        tk.Button(
            self,
            text="...",
            command=self._select_directory,
            width=2,
        ).pack(side="right", padx=(5, 0))

    def _select_directory(self) -> None:
        directory = filedialog.askdirectory(
            parent=self,
            initialdir=self.variable.get(),
            title="Select folder",
        )
        if directory:
            self.variable.set(str(Path(directory)))

    def get(self) -> str:
        return self.variable.get()
