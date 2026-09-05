import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from .saves_tab import SavesTab
from .settings_tab import SettingsTab


class Application:
    """Main application class for the Kingdom New Lands Multisaver."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.report_callback_exception = self._report_callback_exception
        self._configure_window()
        self._create_menu()
        self._create_tabs()

    def _report_callback_exception(self, exc_type, exc_value, exc_traceback) -> None:
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        messagebox.showerror("Error", str(exc_value), parent=self.root)

    def _configure_window(self) -> None:
        self.root.title("Kingdom New Lands Multisaver v1.0")
        self.root.geometry("580x450")
        self.root.minsize(400, 250)

    def _create_menu(self) -> None:
        main_menu = tk.Menu(self.root)
        self.root.config(menu=main_menu)

        file_menu = tk.Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.exit_app)

        help_menu = tk.Menu(main_menu, tearoff=False)
        main_menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def _create_tabs(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        saves_tab = SavesTab(notebook)
        settings_tab = SettingsTab(notebook, on_apply=saves_tab.apply_settings)
        notebook.add(saves_tab, text="Saves")
        notebook.add(settings_tab, text="Settings")

    def exit_app(self) -> None:
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def show_about(self) -> None:
        messagebox.showinfo(
            "About",
            "Kingdom New Lands Multisaver\nVersion 1.0\nAuthor: S4NTY",
            parent=self.root,
        )
