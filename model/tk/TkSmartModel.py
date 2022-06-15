import tkinter as tk
from PIL import ImageTk, Image

class TkSmartModel:

    def __init__(self):
        self.imgLightOn: ImageTk = None
        self.imgLightOff: ImageTk = None
        self.imgBurglar: ImageTk = None
        self.imgNoMovement: ImageTk = None
        self.loadImages()

    def loadImages(self):
        imageLightsOn = Image.open(r"./images/light_on.png")
        imageLightsOff = Image.open(r"./images/light_off.png")
        imageBurglar = Image.open(r"./images/burglar.png")
        imageNoMovement = Image.open(r"./images/no_movement.png")
        self.imgLightOn = ImageTk.PhotoImage(imageLightsOn)
        self.imgLightOff = ImageTk.PhotoImage(imageLightsOff)
        self.imgBurglar = ImageTk.PhotoImage(imageBurglar)
        self.imgNoMovement = ImageTk.PhotoImage(imageNoMovement)