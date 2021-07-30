import requests
import json
from datetime import datetime
import threading
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from dynaconf_settings import settings
from helpers.ArgHandler import Get_Args

from logger.AppLogger import build_logger
logger = build_logger(logger_name="Weather Widget", debug=Get_Args().verbose)

class WeatherWidget(BoxLayout):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    image_prefix = "http://openweathermap.org/img/wn/"
    image_suffix = "@2x.png"

    weather_icon = ObjectProperty()

    def __init__(self, **kwargs):
        # TODO Display city name in this widget
        # TODO Display units in this widget
        self.complete_url = self.base_url + "appid=" + settings.Weather_Widget.get('api_key', 'bbd4a506dfb2384cf85c057a674e92fb') + "&q=" + settings.Weather_Widget.get('city_name', 'New York') + "&units=" + settings.Weather_Widget.get('units', 'imperial')
        self.Get_Weather()

        super(WeatherWidget, self).__init__(**kwargs)

        Clock.schedule_interval(self.Start_Update_Loop, settings.Weather_Widget.get('update_interval', 600))

    def Start_Update_Loop(self, dt):
        update_thread = threading.Thread(target=self.Get_Weather)
        update_thread.setDaemon(True)
        update_thread.start()

    def Update_UI(self, *args):
        self.weather_icon.source = self.Get_Icon()

    def Get_Json_Data(self):
        # TODO Handle api key errors when too many requests happen
        result = requests.get(self.complete_url)

        json_result = result.json()

        if json_result["cod"] != "404":
            return json_result
        else:
            print("Error Code")
            return None

    # TODO: add some error checking here if some of this data does not exist
    def Get_Weather(self):
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