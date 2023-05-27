import requests
import os

def get_current_weather(city):
    OWM_endpoint = "http://api.openweathermap.org/data/2.5/weather"
    API_KEY = os.environ.get("SECRET_KEY_WEATHER")

    weather_params = { 
        'q': city,
        'appid': API_KEY,
        'units': 'metric' 
    }

    try:
        response = requests.get(OWM_endpoint, weather_params)
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            description = data["weather"][0]["description"]
            pressure = data["main"]["pressure"] 
            
            return {
                "temperature": temperature,
                "humidity": humidity,
                "description": description,
                "wind_speed": wind_speed,
                "pressure": pressure
            }
        else:
            print(f"Error: {data['message']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return None

# Example usage
city_name = "London"
weather_info = get_current_weather(city_name)

if weather_info:
    print(f"Weather in {city_name}:")
    print(f"Temperature: {weather_info['temperature']}°C")
    print(f"Humidity: {weather_info['humidity']}%")
    print(f"Wind Speed: {weather_info['wind_speed']} m/s")
    print(f"Description: {weather_info['description']}")
    print(f"Pressure {weather_info['pressure']}")
else:
    print("Failed to retrieve weather information.")
