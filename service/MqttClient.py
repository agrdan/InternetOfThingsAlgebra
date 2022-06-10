from threading import Thread
from time import sleep as delay
import paho.mqtt.client as mqtt
from datetime import datetime as dt
from model.tk.TkConnection import TkConnection
from collections import deque

class MqttClient(Thread):

    def __init__(self, server, port, topic, tkConnectionModel, lblImage):
        Thread.__init__(self)
        self.tkConnectionModel: TkConnection = tkConnectionModel
        self.lblImage = lblImage
        self.mqttClient = mqtt.Client()
        self.server = server
        self.port = port
        self.topic = topic
        self.finished = False
        self.queue = deque()

    def run(self):
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_disconnect = self.on_disconnect
        self.mqttClient.on_subscribe = self.on_subscribe
        self.mqttClient.on_message = self.on_message
        self.mqttClient.connect(host=self.server, port=self.port)
        self.mqttClient.loop_forever()

    def on_connect(self, mqttc, userdata, flags, rc):
        print("Connected...")
        self.tkConnectionModel.connectionStatus.set("Connected")
        self.lblImage.config(image=self.tkConnectionModel.imageConnected)
        mqttc.subscribe(topic=self.topic, qos=0)

    def on_disconnect(self, mqttc, userdata, rc):
        print("Disconnected...")
        self.tkConnectionModel.connectionStatus.set("Disconnected")
        self.lblImage.config(image=self.tkConnectionModel.imageDisconnected)

    def on_subscribe(self, mqttc, userdata, mid, granted_qos):
        print(f"Subscribed to: {self.topic}")

    def on_message(self, mqttc, userdata, msg):
        currentTime = str(dt.now())
        topic = msg.topic
        message = str(msg.payload.decode("utf-8"))
        print(f"{currentTime} | [{topic}]: {message}")
        self.queue.append(f"{topic};{message}")

    def getFromQueue(self):
        if len(self.queue) != 0:
            return self.queue.popleft()
        else:
            return None

    def publish(self, message, topic):
        print(f"Publishing: {message} on topic: {topic}")
        self.mqttClient.publish(topic, message, qos=0, retain=False)

    def disconnect(self):
        self.mqttClient.disconnect()
        self.finished = False
        self.mqttClient = None



