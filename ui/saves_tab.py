import tkinter as tk
from tkinter import messagebox

from config.settings import settings
from core.kingdom_save import KingdomSave
from core.models import SaveEntry
from core.save_manager import SaveManager


class SavesTab(tk.Frame):
    """Saves tab for the application."""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_buttons()
        self._create_panels()
        self._on_init()

    def apply_settings(self) -> None:
        self._save_manager.game_save_dir = settings.GAME_SAVE_DIR
        self._save_manager.saves_dir = settings.SAVES_DIR
        self._update_list_saves()

    def _create_buttons(self) -> None:
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=5)

        tk.Button(
            button_frame, text="Create", command=self._on_create, width=10
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Update", command=self._on_update, width=10
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Restore", command=self._on_restore, width=10
        ).pack(side="left", padx=5)
        tk.Button(
            button_frame, text="Delete", command=self._on_delete, width=10
        ).pack(side="right", padx=5)

    def _create_panels(self) -> None:
        paned_window = tk.PanedWindow(self)
        paned_window.pack(fill="both", expand=True)

        left_panel = tk.Frame(paned_window)
        listbox = tk.Listbox(left_panel, width=40, font="TkDefaultFont", exportselection=False)
        listbox_scrollbar = tk.Scrollbar(
            left_panel, orient="vertical", command=listbox.yview
        )
        listbox.configure(yscrollcommand=listbox_scrollbar.set)
        listbox.bind("<<ListboxSelect>>", self._on_click)
        listbox_scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        paned_window.add(left_panel, width=200)

        right_panel = tk.Frame(paned_window)
        text_area = tk.Text(right_panel, wrap="word", font="TkDefaultFont")
        text_scrollbar = tk.Scrollbar(
            right_panel, orient="vertical", command=text_area.yview
        )
        text_area.configure(yscrollcommand=text_scrollbar.set)
        text_scrollbar.pack(side="right", fill="y")
        text_area.pack(side="left", fill="both", expand=True)
        paned_window.add(right_panel, width=300)

        self._listbox = listbox
        self._text_area = text_area

    def _on_init(self) -> None:
        self._save_manager = SaveManager(game_save_dir=settings.GAME_SAVE_DIR, saves_dir=settings.SAVES_DIR)
        self._update_list_saves()

    def _on_create(self) -> None:
        kingdom_save = KingdomSave(settings.GAME_SAVE_DIR / settings.SAVE_FILE)
        comment = kingdom_save.get_base_data()
        self._save_manager.create_save(comment)
        self._update_list_saves()
        self._text_area.delete("1.0", tk.END)
        self._text_area.insert(tk.END, comment)

    def _on_update(self) -> None:
        save = self._get_selected_save()
        comment = self._text_area.get("1.0", "end-1c")
        save.comment = comment
        self._save_manager.update_save(save, comment)

    def _on_restore(self) -> None:
        save = self._get_selected_save()
        restored_save = self._save_manager.restore_save(save)
        if restored_save is not None:
            messagebox.showinfo(
                "Restore",
                "Save restored.",
                parent=self,
            )

    def _on_delete(self) -> None:
        save = self._get_selected_save()
        save_name = save.path.stem

        if not messagebox.askyesno("Delete save",
            f'Are you sure you want to delete the save "{save_name}"?', parent=self):
            return

        self._save_manager.delete_save(save)
        self._update_list_saves()
        self._text_area.delete("1.0", tk.END)

    def _on_click(self, event) -> None:
        save_entry = self._get_selected_save()
        self._text_area.delete("1.0", tk.END)
        self._text_area.insert(tk.END, save_entry.comment)

    def _get_selected_save(self) -> SaveEntry:
        current_index = self._listbox.curselection()

        if not current_index:
            raise IndexError("Save was not selected.")

        if len(self._saves) <= 0:
            raise IndexError("Saves not found.")

        return self._saves[current_index[0]]

    def _update_list_saves(self) -> list[SaveEntry]:
        self._saves = self._save_manager.list_saves()
        self._listbox.delete(0, tk.END)
        self._text_area.delete("1.0", tk.END)

        for save in self._saves:
            self._listbox.insert(tk.END, save.path.stem)

        return self._saves
