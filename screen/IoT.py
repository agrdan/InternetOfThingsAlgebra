"""
TOPIC iot/general (command get)
TOPIC za upalit/ugasit svijetlo je iot/lights
    command: on/off


"""

from tkinter.ttk import Frame
import tkinter as tk
from tkinter import ttk, filedialog
from model.tk.TkConnection import TkConnection
from service.MqttClient import MqttClient
from PIL import Image, ImageTk
from os import path
from model.tk.TkMessage import TkMessage
from threading import Thread
from time import sleep as delay
from utils.JSONSerializator import JSONSerializator
from datetime import datetime as dt
import base64
from io import BytesIO
from service.CryptoService import CryptoService
import json
from model.tk.TkSmartModel import TkSmartModel
from utils.Utils import Utils



class MessageHandler(Thread):

    def __init__(self, mqtt, messageBox, btnLights, tkSmartModel, lblMovement, tkImageBox):
        Thread.__init__(self)
        self.mqtt = mqtt
        self.messageBox = messageBox
        self.tkImageBox = tkImageBox
        self.receivedImage = False
        self.crypto = CryptoService()
        self.btnLights: ttk.Button = btnLights
        self.lblMovement: ttk.Label = lblMovement
        self.tkSmartModel: TkSmartModel = tkSmartModel
        self.lightState = None

    def run(self):
        while True:
            value = self.mqtt.getFromQueue()
            if value is not None:
                try:
                    topic, message = value.split(";")
                    if topic == "iot/image":
                        print("been here")
                        imageModel = JSONSerializator().serialize(message)
                        imgDecoded = base64.b64decode(imageModel.image)
                        img = Image.open(BytesIO(imgDecoded))
                        if self.receivedImage:
                            self.imageReceived.destroy()
                            self.imageReceived = None
                        tkImage = ImageTk.PhotoImage(img)
                        self.imageReceived = ttk.Label(self.tkImageBox, image=tkImage)
                        self.imageReceived.grid(row=1, column=2, pady=5, padx=5)
                        self.imageReceived.image = tkImage
                        self.receivedImage = True
                    # decrypt = self.crypto.decrypt(message, "iotenkripcija")
                    # model = JSONSerializator().serialize(decrypt)
                    model = JSONSerializator().serialize(message)
                    toPrint = f"temperature: {model.temperature}\n" \
                              f"pressure: {model.pressure}\n" \
                              f"humidity: {model.humidity}"
                    self.lightState = model.light
                    if model.light:
                        self.btnLights.config(image=self.tkSmartModel.imgLightOn)
                    else:
                        self.btnLights.config(image=self.tkSmartModel.imgLightOff)

                    currentTime = dt.now()
                    lastMovement = Utils.createDateFromString(model.lastMotionDetected)
                    diff = currentTime - lastMovement
                    if int(diff.seconds) > 60:
                        self.lblMovement.config(image=self.tkSmartModel.imgNoMovement)
                    else:
                        self.lblMovement.config(image=self.tkSmartModel.imgBurglar)


                    messageToPrint = f"\n<{dt.now()}>\n[{topic}]: \n{toPrint}"
                    self.writeToMessageBox(messageToPrint)
                except:
                    pass
            delay(1)

    def getConfig(self):
        self.mqtt.publish("get", "iot/general")

    def toggleLights(self):
        self.lightState = None
        self.getConfig()
        while self.lightState is None:
            pass

        if self.lightState is not None:
            if self.lightState:
                self.mqtt.publish("off", "iot/lights")
                #self.btnLights.config(image=self.tkSmartModel.imgLightOff)
            else:
                self.mqtt.publish("on", "iot/lights")
                #self.btnLights.config(image=self.tkSmartModel.imgLightOn)
        else:
            self.writeToMessageBox("Response timeout")
        #delay(2)
        #self.getConfig()

    def writeToMessageBox(self, message):
        self.messageBox.config(state=tk.NORMAL)
        self.messageBox.insert(tk.END, message + "\n")
        self.messageBox.config(state=tk.DISABLED)
        self.messageBox.see(tk.END)



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
            while not self.mqtt.mqttClient.is_connected():
                pass
            self.connectionTriggered = True
            self.btnConnect.config(text="Disconnect")
            self.appTabs = ttk.Notebook(self)
            self.appTabs.grid(row=0, column=1, pady=5, padx=5, sticky=tk.N)
            self.tabMessages = ttk.Frame(self.appTabs)
            self.tabSmartHome = ttk.Frame(self.appTabs)
            self.appTabs.add(self.tabMessages, text="Messages")
            self.appTabs.add(self.tabSmartHome, text="Smart Home")
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
        self.smartPanel.destroy()
        self.appTabs.destroy()

    def createMessagePanel(self):
        self.commands = []
        self.setCommands()

        self.tkMessage = TkMessage()
        messagePanel = ttk.LabelFrame(self.tabMessages, text="Message panel")
        messagePanel.grid(row=0, column=0, padx=15, pady=5, sticky=tk.N)

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

        self.receivePanel = ttk.LabelFrame(self.tabMessages, text="Receive message panel")
        self.receivePanel.grid(row=0, column=2, padx=15, pady=5, sticky=tk.N)

        self.receiveMessageBox = tk.Text(self.receivePanel, width=60)
        self.receiveMessageBox.grid(row=0, column=0, pady=5, padx=5, columnspan=3)
        self.receiveMessageBox.config(state=tk.DISABLED)
        self.createSmartPanel()

        self.messageHandler = MessageHandler(self.mqtt, self.receiveMessageBox, self.btnLights, self.tkSmartModel, self.lblMovement, self.tkImageBox)
        self.messageHandler.start()

        self.messageHandler.getConfig()

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

    # _____________________________________ /MessagePanel

    # _____________________________________SmartPanel
    def createSmartPanel(self):

        # self.rowconfigure(1, weight=1)
        # self.columnconfigure(0, weight=1)
        self.tkSmartModel = TkSmartModel()
        self.smartPanel = ttk.Labelframe(self.tabSmartHome, text="Smart panel")
        self.smartPanel.grid(row=0, column=0, pady=5, padx=5, sticky=tk.N)

        self.btnLights = ttk.Button(self.smartPanel, image=self.tkSmartModel.imgLightOff, command=self.toggleLight)
        self.btnLights.grid(row=0, column=0, pady=5, padx=5)

        self.lblMovement = ttk.Label(self.smartPanel, image=self.tkSmartModel.imgNoMovement)
        self.lblMovement.grid(row=0, column=1, padx=5, pady=5)

        self.createImageBox()

    def toggleLight(self):
        self.messageHandler.toggleLights()

    def createImageBox(self):

        self.tkImageBox = ttk.LabelFrame(self.tabSmartHome, text="Image box")
        self.tkImageBox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)

        self.btnBrowse = ttk.Button(self.tkImageBox, command=self.browse, text="Browse")
        self.btnBrowse.grid(row=0, column=0, pady=5, padx=5, sticky=tk.W)

        self.btnPublishImage = ttk.Button(self.tkImageBox, text="Publish image", command=self.publishImage)
        self.btnPublishImage.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)
        self.btnPublishImage.config(state="disabled")
        self.imageBox = None


    def publishImage(self):
        if self.image is not None:

            bufferedImage = BytesIO()
            converted = self.image.convert("RGB")
            converted.save(bufferedImage, "JPEG")
            b64Image = base64.b64encode(bufferedImage.getvalue())
            jsonModel = {
                "image": str(b64Image, "utf-8")
            }
            self.mqtt.publish(json.dumps(jsonModel), "iot/image")

    def browse(self):
        if self.imageBox is not None:
            self.imageBox.destroy()
            self.imageBox = None
            self.image = None
        self.file = filedialog.askopenfile(parent=self, mode="rb", title="Choose a file")
        self.image = Image.open(self.file)
        if self.image is not None:
            self.btnPublishImage.config(state="enabled")
            tkImage = ImageTk.PhotoImage(self.image)
            if self.imageBox is None:
                self.imageBox = ttk.Label(self.tkImageBox, image=tkImage)
                self.imageBox.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
                self.imageBox.image = tkImage

    # _____________________________________ /SmartPanel






















