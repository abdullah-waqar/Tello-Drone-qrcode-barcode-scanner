import cv2
import numpy as np
from pyzbar.pyzbar import decode
from djitellopy import tello
from threading import Thread
import pyaudio
from vosk import Model, KaldiRecognizer

tello = tello.Tello()

tello.connect()
print(tello.get_battery())
tello.streamon()

keepScanning = True

model = Model(r"C:\Users\Abdullah\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

def videoStreaming():
    while keepScanning:
        img = tello.get_frame_read().frame
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            
            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img, [pts] , True, (255,0,255), 5)
            pts2 = barcode.rect
            cv2.putText(img, myData, (pts2[0] , pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,255), 1 )
        
        cv2.imshow('Result ', img)
        cv2.waitKey(1)
        

def speechRecognizer():
    data = stream.read(4096)
    if recognizer.AcceptWaveform(data):
        text = recognizer.Result()
        return (text[14:-3])

def voiceDetection():
    while True:
        text  = speechRecognizer()
        if text == 'take off' or text == 'move up':
            print("drone is taking off")
            tello.takeoff()
        elif text == 'land':
            print("Drone is landing")
            tello.land()
        # else:
        #     print(text)

scanner = Thread(target=videoStreaming)
voiceThread = Thread(target=voiceDetection)

scanner.start()
voiceThread.start()

scanner.join()
scanner.join()
