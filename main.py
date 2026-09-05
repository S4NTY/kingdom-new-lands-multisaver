import tkinter as tk

from ui.app import Application
from config.settings import settings

def main():
    root = tk.Tk()
    settings.load()
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
