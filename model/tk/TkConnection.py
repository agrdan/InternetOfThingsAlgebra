import tkinter as tk
from PIL import ImageTk


class TkConnection:

    def __init__(self):
        self.url = tk.StringVar()
        self.port = tk.StringVar()
        self.topic = tk.StringVar()
        self.saveServerInfo = tk.BooleanVar()
        self.connectionStatus = tk.StringVar()
        self.imageConnected: ImageTk = None
        self.imageDisconnected: ImageTk = None