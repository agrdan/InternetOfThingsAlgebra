from tkinter.ttk import Frame
import tkinter as tk
from tkinter import ttk
from model.tk.TkConnection import TkConnection
from service.MqttClient import MqttClient

class IoT(Frame):

    def __init__(self, container):
        super().__init__(container)
        self.grid()
        self.tkConnectionModel = TkConnection()
        self.createConnectionPanel()

    def createConnectionPanel(self):

        connectionPanel = ttk.LabelFrame(self, text="Server connection")
        connectionPanel.grid(row=0, column=0, padx=5, pady=5)

        serverUrlLbl = ttk.Label(connectionPanel, text="Server URL: ")
        serverUrlLbl.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        serverUrl = ttk.Entry(connectionPanel, textvariable=self.tkConnectionModel.url, width=40)
        serverUrl.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)
        #_____
        serverPortLbl = ttk.Label(connectionPanel, text="Server port: ")
        serverPortLbl.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        serverPort = ttk.Entry(connectionPanel, textvariable=self.tkConnectionModel.port)
        serverPort.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)
        #_____
        serverTopicLbl = ttk.Label(connectionPanel, text="Topic: ")
        serverTopicLbl.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        serverTopic = ttk.Entry(connectionPanel, textvariable=self.tkConnectionModel.topic)
        serverTopic.grid(row=2, column=1, pady=5, padx=5, sticky=tk.EW)

        btnConnect = ttk.Button(connectionPanel, command=self.connect, text="Connect")
        btnConnect.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)


    def connect(self):
        mqtt = MqttClient(self.tkConnectionModel.url.get(), int(self.tkConnectionModel.port.get()), self.tkConnectionModel.topic.get())
        mqtt.start()