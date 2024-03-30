import json
import streamlit as st
import cv2
import numpy as np
import requests
import sqlite3
from streamlit_option_menu import option_menu
import pandas as pd
from utils import key, url


user_color = '#000000'
title_webapp = "AI-Driven Automated Parking System"
html_temp = f"""
            <div style="background-color:{user_color};padding:12px">
            <h1 style="color:white;text-align:center;">{title_webapp}</h1>
            </div>
            """

st.markdown(html_temp, unsafe_allow_html=True)
conn = sqlite3.connect('car_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS car_data
             (plate TEXT, in_time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS user_details
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             license_plate TEXT, 
             user_name TEXT,
             mobile_number TEXT,
             car_model TEXT,
             registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             parking_status TEXT DEFAULT 'IN')''')
conn.commit()

def insert_car_data(plate, in_time):
    c.execute("INSERT INTO car_data (plate, in_time) VALUES (?, ?)", (plate, in_time))
    conn.commit()

def fetch_car_data():
    c.execute("SELECT * FROM car_data")
    return c.fetchall()

def main():

    selected_menu = option_menu(None, ['Manual Entry', 'View Visitor History', 'Register user'], icons=['camera', "clock-history", 'person-plus'], menu_icon="cast", default_index=0, orientation="horizontal")

    if selected_menu == 'Manual Entry':
        st.warning("Automated system in working")
        # Reading Camera Image
        # frame = st.camera_input("Take a picture")
        # if frame is not None:
        #     files = {"upload": frame}
        #     headers = {"Authorization": f"Token {key}"}
        #     response = requests.post(url, files=files, headers=headers)
        #     response_data = json.loads(response.text)
        #     st.write(response_data)
        #     car_number = response_data['results'][0]['plate']
        #     timestamp = response_data['timestamp']
        #     st.write(car_number)
        #     st.write(timestamp)
        #     insert_car_data(car_number, timestamp)
        #     st.success('Car Registered Sucessfully')

    if selected_menu == 'View Visitor History':
        st.header("DataBase Entry")
        car_data = fetch_car_data()
        st.write("Car Data in Database")
        df = pd.DataFrame(car_data, columns=['plate', 'in_time'])
        st.write(df)

    if selected_menu == 'Register user':
        license_plate = st.text_input('Enter License Plate Number')
        user_name = st.text_input('Enter User Name')
        mobile_number = st.text_input('Enter Mobile Number')
        car_model = st.text_input('Enter Car Model')
        # Save button
        if st.button('Save'):
            # Check if the car is already registered
            c.execute("SELECT * FROM user_details WHERE license_plate=?", (license_plate,))
            existing_entry = c.fetchone()
            
            if existing_entry:
                st.warning('Car is already registered')
            else:
                # If the car is being registered for the first time, mark parking status as "IN"
                c.execute("INSERT INTO user_details (license_plate, user_name, mobile_number, car_model) VALUES (?, ?, ?, ?)",
                        (license_plate, user_name, mobile_number, car_model))
                conn.commit()
                st.success('Car details saved successfully with IN status.')

        # View Data option
        if st.button('View Data'):
            # Fetch data from the database
            c.execute("SELECT * FROM user_details")
            data = c.fetchall()
            if data:
                # Display data in a table format
                df = pd.DataFrame(data, columns=['ID', 'License Plate', 'User Name', 'Mobile Number', 'Car Model', 'Registration Time', 'Parking Status'])
                st.write(df)
            else:
                st.warning('No data found in the database.')
                
if __name__ == "__main__":
    main()