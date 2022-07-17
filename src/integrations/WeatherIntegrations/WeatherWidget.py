import requests
import json
from datetime import datetime
import threading
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from dynaconf_settings import settings
from helpers.ArgHandler import Get_Args

from logger.AppLogger import build_logger
logger = build_logger(logger_name="Weather Widget", debug=Get_Args().verbose)

default_update_interval = 600

class WeatherWidget(RelativeLayout):
    """A weather widget to display weather data including current temperature, 
    a 'feels like' temperature, and an icon for current conditions
    """

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    image_prefix = "http://openweathermap.org/img/wn/"
    image_suffix = "@2x.png"

    weather_icon = ObjectProperty()

    def __init__(self, **kwargs):
        # TODO Display city name in this widget
        # TODO Display units in this widget
        self.complete_url = self.base_url + "appid=" + settings.Weather_Widget.api_key + "&q=" + settings.Weather_Widget.get('city_name', 'New York') + "&units=" + settings.Weather_Widget.get('units', 'imperial')
        self.Get_Weather()

        super(WeatherWidget, self).__init__(**kwargs)

        Clock.schedule_interval(self.Start_Update_Loop, settings.Weather_Widget.get('update_interval', default_update_interval))

    def Start_Update_Loop(self, dt):
        """Start a new thread to handle updating the weather widget"""

        update_thread = threading.Thread(target=self.Get_Weather)
        update_thread.setDaemon(True)
        update_thread.start()

    def Update_UI(self, *args):
        """Update the UI by setting the icon and forcing the image to reload"""

        self.weather_icon.source = self.Get_Icon()
        self.weather_icon.reload()

    def Get_Json_Data(self):
        """Make an API call to OpenWeatherMap and return the result as JSON"""
        
        # TODO Handle api key errors when too many requests happen
        result = requests.get(self.complete_url)

        json_result = result.json()

        if json_result["cod"] != "404":
            return json_result
        else:
            print("Error Code")
            return None

    def Get_Weather(self):
        """Using the JSON data provided by 'Get_Json_Data', set the appropriate fields of the widget"""

        # TODO: add some error checking here if some of this data does not exist
        logger.info("Pulling weather data")
        json_data = self.Get_Json_Data()
        if json_data:
            self.location = json_data["name"]
            self.description = json_data["weather"][0]["description"]
            main = json_data["main"]
            self.temperature = main["temp"]
            self.feels_like = main["feels_like"]
            self.icon_url = self.image_prefix + json_data["weather"][0]["icon"] + self.image_suffix
            # Schedule the icon to populate itself next frame
            Clock.schedule_once(self.Update_UI, 0)

    def Get_Temp(self):
        return self.temperature
    
    def Get_Location(self):
        return self.location
    
    def Get_Desc(self):
        return self.description

    def Get_Feels(self):
        return self.feels_like

    def Get_Icon(self):
        return self.icon_url