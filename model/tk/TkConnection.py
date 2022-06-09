import tkinter as tk


class TkConnection:

    def __init__(self):
        self.url = tk.StringVar()
        self.port = tk.StringVar()
        self.topic = tk.StringVar()
