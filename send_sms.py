import psycopg2
import requests
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import sys
from dotenv import load_dotenv
import logging
from opencage.geocoder import OpenCageGeocode

OWM_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
account_sid = "ACdf0647ef43e29f89e08d929590bcecbc"

PROJECT_FOLDER = os.path.expanduser('~')

load_dotenv(os.path.join(PROJECT_FOLDER, '.env'))

API_KEY = os.getenv("SECRET_KEY_WEATHER")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
OCG_API_KEY = os.getenv("OCG_API_KEY")

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
        print("No results found for the city:", city_name)
        return None, None                    

def send_sms(phone_number, message_body):
    message_body = message_body
    phone_number = phone_number

    # Configure logging
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    try:
        query = "SELECT phone_number FROM users"
        phone_numbers = manage_connection(query) #try to fetch the phone numbers from db
        try:
            client = Client(account_sid, AUTH_TOKEN)
            for phone_number in phone_numbers:
                message = client.messages.create( # Create and send SMS for each phone number
                body=message_body,
                from_='+13158186457',  
                to=phone_number[0]  # Extract the phone number from the fetched result
            )
            print("Message sent to:", phone_number[0], "Status:", message.status)

        except TwilioException as sms_exception:
            logging.exception("Error sending SMS")# Log the SMS sending exception
            print("Error sending SMS:", str(sms_exception))

    except Exception as db_exception:
        logging.exception("Error connecting to the database")# Log the database connection exception
        print("Error connecting to the database:", str(db_exception))

def get_weather_data(latitude, longitude):
    weather_params = { 
    'lat': latitude,
    'lon': longitude,
    'appid': API_KEY,
    'units': 'metric' # for temp in Celsius
    }

    try:
        # Send API request
        response = requests.get(OWM_endpoint, params = weather_params)
        response.raise_for_status()

        # Check if the request was successful
        if response.status_code == 200:

            # Exstract weather data
            weather_data = response.json() 
            weather_clice = weather_data['list'][:4] #we need only the forecast for the next 12 hours(the step in forecast is 3 hours).

            will_rain = False
            will_snow = False
            will_fog = False
            will_sand = False
            will_clear = False
            will_cloudy = False
            will_squall = False
            will_tornado = False
            min_temp = weather_clice[0]['main']['temp_min'] #min temp of the first slice. we will compare it with min_temp of the next 3 slices and choose the absolute min temp.
            max_temp = weather_clice[0]['main']['temp_max'] 
        

            for hour_data in weather_clice: #loop through the 4 clices
                for sublist in hour_data['weather']: # sometimes [weather] have more than one sublist. it can be rain and fog at the same time
                    condition_code = sublist['id']
                    print (condition_code) # for check
                    print(len(hour_data['weather'])) # for check
                    if condition_code < 600:
                        will_rain = True
                    if 600 <= condition_code <= 622:
                        will_snow = True
                    if 701 <= condition_code <= 721 or condition_code == 741:
                        will_fog = True
                    if condition_code == 731 or condition_code == 751 or condition_code == 761:
                        will_sand = True
                    if 800 <= condition_code < 804:
                        will_clear = True
                    if condition_code == 771:
                        will_squall = True
                    if condition_code == 781:
                        will_tornado = True
                    if condition_code == 804:
                        will_cloudy = True

                if hour_data['main']['temp_min'] < min_temp:
                    min_temp = hour_data['main']['temp_min'] 
                if hour_data['main']['temp_max'] > max_temp:
                    max_temp = hour_data['main']['temp_max'] 

            if will_snow or will_rain or will_cloudy or will_squall or will_tornado or will_fog or will_sand:
                will_clear = False # if in any time of the day will be one of these conditions, we cant say that the day will be clear. even if in one of the slices became to be True. 
            
            # create the message body
            message_body = ""

            if will_rain:
                message_body += "It's going to rain today. Remember to bring an ☔️."

            if will_sand:
                message_body += "There will be sandstorm. Take necessary precautions."

            if will_fog:
                message_body += "Expect foggy conditions. Drive carefully."

                if will_snow:
                    message_body += "Expect snowfall today. Bundle up and stay warm! ❄️"

            if will_clear:
                message_body += "It will be clear skies today. Enjoy the sunshine! ☀️"

            if will_cloudy:
                message_body += "Cloudy conditions are expected. Keep an eye on the sky and dress accordingly. ☁️"

            if will_squall:
                message_body += "There will be squally weather. Stay indoors and stay safe! 🌪️"

            if will_tornado:
                message_body += "A tornado warning has been issued. Seek shelter immediately! 🌪️"

            # Include temperature information
            message_body += f" The temperature will range from {round(min_temp)}°C to {round(max_temp)}°C."    

            print(message_body)
            return message_body
            
    except Exception as e:
        print(f'Error occurred: {str(e)}')

def send_weather_notifications():
    try:
        # Connect to the PostgreSQL database and retrieve latitude and longitude for each user
        query = f"SELECT latitude, longitude, phone_number FROM users"
        users = manage_connection(query)

        for user in users:
            latitude, longitude, phone_number = user

            try:
                # Call OpenWeatherMap API to get weather data and create message
                message_body = get_weather_data(latitude, longitude) 

                # Send SMS notification to the user
                send_sms(phone_number, message_body)
            except:
                pass # i need to check what to do here....

    except Exception as db_exception:
        logging.exception("Error connecting to the database")# Log the database connection exception
        print("Error connecting to the database:", str(db_exception))

send_weather_notifications()