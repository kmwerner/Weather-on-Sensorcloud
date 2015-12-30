# -*- coding: utf-8 -*-

import pyowm

def get_current_weather(airportCode):
    
    "Get the current weather. Input the city's airport code, e.g. BTV"
    apiKey='your-api-key-goes-here'
    owm = pyowm.OWM(apiKey)
    
    observation = owm.weather_at_place(str(airportCode)) #observe current weather
    tempF = observation.get_weather().get_temperature('fahrenheit')['temp']
    time = observation.get_reception_time()
    return(tuple([time,tempF]))

