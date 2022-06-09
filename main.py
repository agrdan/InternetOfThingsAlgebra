import tkinter as tk
from tkinter import ttk
from screen.IoT import IoT

SERVER = "edu-agrdan.plusvps.com"
PORT = 1883 # 8883
TOPIC = "predavac"

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.geometry("700x900")
        self.title("IoT Portal")

        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container['relief'] = tk.RIDGE
        self.container['borderwidth'] = 7
        self.createIoT()

    def createIoT(self):
        # poziv klase s novim prozorom koji ce biti loadan u containter
        IoT(self.container)




if __name__ == '__main__':
    app = App()
    app.mainloop()



