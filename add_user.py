from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
import psycopg2
from opencage.geocoder import OpenCageGeocode
import os
import string

OCG_API_KEY = os.getenv("OCG_API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")

message_body = 'A tornado warning has been issued. Seek shelter immediately! 🌪️'

def manage_connection(query):
        connection = psycopg2.connect(
            host="localhost",
            port = '5432', 
            database="Weather",
            user="postgres",
            password=DB_PASSWORD
        )

        with connection:
            with connection.cursor() as cursor:  
                 if "SELECT" in query:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    return result
                 else:
                    cursor.execute(query)
                    connection.commit()

def get_latitude_longitude(city_name):
    api_key = OCG_API_KEY

    geocoder = OpenCageGeocode(api_key)#create an instance of OpenCageGeocoder

    results = geocoder.geocode(city_name)

    if results and len(results):
        latitude = results[0]['geometry']['lat']
        longitude = results[0]['geometry']['lng']
        return latitude, longitude
    else:
        return None, None                    

def add_user():

    first_name = input("Enter first name: ").title()
    last_name = input("Enter last name: ").title()
    phone_number = input("Enter phone number: ")# TODO: check the number is valid and in the right format. and...verification code? hint text with the right format example.
    city_name = input("Enter city name: ").title()# TODO: validation

    if not all([first_name, last_name, phone_number, city_name]):
        print("Invalid input. Please provide all the required information.")
        return

    # Retrieve latitude and longitude coordinates
    latitude, longitude = get_latitude_longitude(city_name)
    if latitude is None or longitude is None:
        print("Could not retrieve geographical coordinates for your city. Please check the city name.")
        return

    # Insert the new user into the 'users' table
    query = '''
        INSERT INTO users (first_name, last_name, phone_number, city, latitude, longitude)
        VALUES ('%s', '%s', '%s', '%s', %s, %s)
    '''
    query = query % (first_name, last_name, phone_number, city_name, latitude, longitude)
    manage_connection(query)

    print("User added successfully.")


# add_user()
# send_sms("Expect snowfall today. Bundle up and stay warm! ❄️")   
print(get_latitude_longitude('Tel Aviv'))


