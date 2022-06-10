from tkinter.ttk import Frame
import tkinter as tk
from tkinter import ttk
from model.tk.TkConnection import TkConnection
from service.MqttClient import MqttClient
from PIL import Image, ImageTk
from os import path
from model.tk.TkMessage import TkMessage
from threading import Thread
from time import sleep as delay
from utils.JSONSerializator import JSONSerializator
from datetime import datetime as dt

class MessageHandler(Thread):

    def __init__(self, mqtt, messageBox):
        Thread.__init__(self)
        self.mqtt = mqtt
        self.messageBox = messageBox

    def run(self):
        while True:
            value = self.mqtt.getFromQueue()
            if value is not None:
                topic, message = value.split(";")
                model = JSONSerializator().serialize(message)
                toPrint = f"temperatura: {model.temperature}\n" \
                          f"pressure: {model.pressure}\n" \
                          f"humidity: {model.humidity}"
                self.messageBox.config(state=tk.NORMAL)
                messageToPrint = f"\n<{dt.now()}>\n[{topic}]: \n{toPrint}"
                self.messageBox.insert(tk.END, messageToPrint + "\n")
                self.messageBox.config(state=tk.DISABLED)
                self.messageBox.see(tk.END)
            delay(1)


class IoT(Frame):
    FILE_NAME = "serverInfo.txt"

    def __init__(self, container):
        super().__init__(container)
        self.grid()
        self.tkConnectionModel = TkConnection()
        self.createConnectionPanel()
        self.connectionTriggered = False

    # _____________________________________ConnectionPanel

    def createConnectionPanel(self):

        connectionPanel = ttk.LabelFrame(self, text="Server connection")
        connectionPanel.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N)

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

        cbSaveServerInfo = ttk.Checkbutton(connectionPanel, text="Save server info", variable=self.tkConnectionModel.saveServerInfo)
        cbSaveServerInfo.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)

        self.btnConnect = ttk.Button(connectionPanel, command=self.connect, text="Connect")
        self.btnConnect.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.tkConnectionModel.connectionStatus.set("Disconnected")
        lblStatusMessage = ttk.Label(connectionPanel, textvariable=self.tkConnectionModel.connectionStatus)
        lblStatusMessage.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        imageConnected = Image.open(r"./images/connected.png")
        imageDisconnected = Image.open(r"./images/disconnected.png")
        self.tkConnectionModel.imageConnected = ImageTk.PhotoImage(imageConnected)
        self.tkConnectionModel.imageDisconnected = ImageTk.PhotoImage(imageDisconnected)
        self.lblStatusImage = ttk.Label(connectionPanel, image=self.tkConnectionModel.imageDisconnected)
        self.lblStatusImage.grid(row=5, column=1, pady=5, padx=5, sticky=tk.E)

        # 1 redku file-a nalazi serverUrl;port ";"
        if path.exists(self.FILE_NAME):
            f = open(self.FILE_NAME)
            line = f.readline()
            f.close()
            url, port = line.split(";")
            if url != "" and port != "":
                self.tkConnectionModel.url.set(url)
                self.tkConnectionModel.port.set(port)
                self.tkConnectionModel.saveServerInfo.set(True)


    def connect(self):
        if not self.connectionTriggered:
            serverUrl = self.tkConnectionModel.url.get()
            serverPort = self.tkConnectionModel.port.get()
            serverTopic = self.tkConnectionModel.topic.get()

            if self.tkConnectionModel.saveServerInfo.get():
                with open(self.FILE_NAME, "w") as f:
                    f.write(f"{serverUrl};{serverPort}")
                    f.close()
            else:
                with open(self.FILE_NAME, "w") as f:
                    f.write(f";")
                    f.close()

            defaultPort = True
            if serverPort != "":
                defaultPort = False

            if not defaultPort:
                port = int(serverPort)
            else:
                port = 1883

            self.mqtt = MqttClient(serverUrl, port, serverTopic, self.tkConnectionModel, self.lblStatusImage)
            self.mqtt.start()

            self.connectionTriggered = True
            self.btnConnect.config(text="Disconnect")
            self.createMessagePanel()
        else:
            self.mqtt.disconnect()
            self.mqtt = None
            self.connectionTriggered = False
            self.btnConnect.config(text="Connect")
            self.destroyMessagePanel()


    # _____________________________________/ConnectionPanel

    # _____________________________________MessagePanel
    def destroyMessagePanel(self):
        self.messagePanel.destroy()
        self.receivePanel.destroy()

    def createMessagePanel(self):
        self.commands = []
        self.setCommands()

        self.tkMessage = TkMessage()
        messagePanel = ttk.LabelFrame(self, text="Message panel")
        messagePanel.grid(row=0, column=1, padx=15, pady=5)

        self.messagePanel = messagePanel

        self.messageBox = tk.Text(messagePanel, width=60)
        self.messageBox.grid(row=0, column=0, pady=5, padx=5, columnspan=3)
        self.messageBox.config(state=tk.DISABLED)

        entryMessage = ttk.Entry(messagePanel, textvariable=self.tkMessage.message)
        entryMessage.grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW, columnspan=3)
        entryMessage.bind("<Return>", self.sendMessageEvent)
        entryMessage.bind("<Up>", self.arrowUp)
        entryMessage.bind("<Down>", self.arrowDown)

        lblTopic = ttk.Label(messagePanel, text="Publish on topic: ")
        lblTopic.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        entryTopic = ttk.Entry(messagePanel, textvariable=self.tkMessage.topic)
        entryTopic.grid(row=2, column=1, pady=5, padx=5, sticky=tk.EW)

        btnSend = ttk.Button(messagePanel, text="Send", command=self.sendMessage)
        btnSend.grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)

        self.receivePanel = ttk.LabelFrame(self, text="Receive message panel")
        self.receivePanel.grid(row=0, column=2, padx=15, pady=5, sticky=tk.N)

        self.receiveMessageBox = tk.Text(self.receivePanel, width=60)
        self.receiveMessageBox.grid(row=0, column=0, pady=5, padx=5, columnspan=3)
        self.receiveMessageBox.config(state=tk.DISABLED)

        self.messageHandler = MessageHandler(self.mqtt, self.receiveMessageBox)
        self.messageHandler.start()

    def setCommands(self):
        self.commandIndex = len(self.commands)

    def arrowUp(self, event):
        if self.commandIndex > 0:
            self.commandIndex -= 1
            self.tkMessage.message.set(self.commands[self.commandIndex])

    def arrowDown(self, event):
        if self.commandIndex < len(self.commands):
            self.commandIndex += 1
            if self.commandIndex == len(self.commands):
                self.tkMessage.message.set("")
            else:
                self.tkMessage.message.set(self.commands[self.commandIndex])

    def sendMessageEvent(self, event):
        self.sendMessage()

    def sendMessage(self):
        if self.tkMessage.message.get().strip() != "" and self.tkMessage.topic.get().strip() != "":
            message = self.tkMessage.message.get()
            topic = self.tkMessage.topic.get()
            self.mqtt.publish(message, topic)
            self.messageBox.config(state=tk.NORMAL)
            messageToPrint = f"[{topic}]: {message}"
            self.messageBox.insert(tk.END, messageToPrint + "\n")
            self.messageBox.config(state=tk.DISABLED)
            self.messageBox.see(tk.END)
            self.commands.append(message)
            self.tkMessage.message.set("")
            self.setCommands()





















