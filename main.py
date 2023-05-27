import requests
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import sys
from dotenv import load_dotenv

OWM_endpoint = "https://api.openweathermap.org/data/2.5/forecast"
account_sid = "ACdf0647ef43e29f89e08d929590bcecbc"

PROJECT_FOLDER = os.path.expanduser('~')

load_dotenv(os.path.join(PROJECT_FOLDER, '.env'))

API_KEY = os.getenv("SECRET_KEY_WEATHER")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

weather_params = { # Givat Ada - place i live. clear
    'lat': 32.524529,
    'lon': 34.941971,
    'appid': API_KEY,
    'units': 'metric' # for temp in Celsius
    }

# 'lat': 68.360741,
# 'lon': -133.723022, # inuvik - place in canada where cloudy now

# 'lat': 60.583333333333336, # place with snow today
# 'lon': -140.96666666666667,

# 'lat': 4.710989,# bogota where is rain today
# 'lon': -74.072090,

try:
    # Send API request
    response = requests.get(OWM_endpoint, params = weather_params)
    response.raise_for_status()

    # Check if the request was successful
    if response.status_code == 200:

        # --------------------------------Extract the desired information----------------#

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
                if  800 <= condition_code < 804:
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
            will_clear = False # if in any time of the day will be one of these conditions, we cant say that the day will be clear. even if in one of the slices will_clear became to be True. 
 
        print (min_temp)  
        print (max_temp)     
        print (f"will_clear: {will_clear}")   
        print (f"will_rain: {will_rain}")  
        print (f"will_snow: {will_snow}")    
        print (f"will_sand: {will_sand}") 
        print (f"will_cloudy: {will_cloudy}") 
        print (f"will_squall: {will_squall}") 
        print (f"will_tornado: {will_tornado}")

#-----------------------------create the message body------------------------#

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

# -----------------------------sending SMS------------------------#
        try:
            client = Client(account_sid, AUTH_TOKEN)
            message = client.messages \
                .create(
                        body= message_body,
                        from_='+13158186457',
                        to='+972526000164'
                    )
            print(message.status)

        except TwilioException as e:
            print("Error sending SMS:", str(e))

# Handle any exceptions that occur during the API request
except Exception as e:
    print(f'Error occurred: {str(e)}')











# print(weather_data['list'][0]['weather'][0]['id'])






