import cv2
import requests
import datetime
from ultralytics import YOLO
import json
import streamlit as st
import sqlite3
import pandas as pd
from utils import key, url
import win32com.client as wincl

vehical_model = YOLO("yolov8n.pt")

conn = sqlite3.connect('car_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS car_data (plate TEXT, in_time TEXT)''')
conn.commit()

def insert_car_data(plate, in_time):
    c.execute("INSERT INTO car_data (plate, in_time) VALUES (?, ?)", (plate, in_time))
    conn.commit()

def fetch_car_data():
    c.execute("SELECT * FROM car_data")
    return c.fetchall()

def speak(text):
    speaker = wincl.Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

def main():
    # Create a VideoCapture object
    frame_num = 2
    ret = True
    vehicles = [2, 3, 5, 7]
    cap = cv2.VideoCapture(0)  # 0 corresponds to the default camera, change it if you have multiple cameras
    while True:
        # Capture frame-by-frame
        frame_num += 1
        ret, frame = cap.read()
        if ret and frame_num%10==0 :
            detections_generator = vehical_model(frame, verbose=False)[0]
            for detection in detections_generator.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if ( int(class_id) in vehicles ) :
                    speak("Welcome, We are Making the entry of your car")
                    _, img_encoded = cv2.imencode('.jpg', frame)
                    files = {"upload": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
                    headers = {"Authorization": f"Token {key}"}
                    response = requests.post(url, files=files, headers=headers)
                    response_data = json.loads(response.text)
                    if response_data['results']:
                        car_number = response_data['results'][0]['plate']
                        timestamp = response_data['timestamp']
                        st.write(car_number)
                        st.write(timestamp)
                        insert_car_data(car_number, timestamp)
                    speak("Data saved, Please park you car")

        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)
        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
