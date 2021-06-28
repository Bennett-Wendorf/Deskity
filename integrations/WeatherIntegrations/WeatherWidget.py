import requests
import json
import time
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class WeatherWidget(BoxLayout):
    # TODO Add this API key to a config file
    api_key = "bbd4a506dfb2384cf85c057a674e92fb"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    image_prefix = "http://openweathermap.org/img/wn/"
    image_suffix = "@2x.png"

    units = "imperial"

    weather_icon = ObjectProperty()

    def __init__(self, **kwargs):
        #TODO: This will need to be set somehow, probably in configuration files
        self.city_name = "Stevens Point"
        self.complete_url = self.base_url + "appid=" + self.api_key + "&q=" + self.city_name + "&units=" + self.units
        self.Get_Weather()

        # Schedule the icon to populate itself next frame
        Clock.schedule_once(self.Update_UI, 0)

        super(WeatherWidget, self).__init__(**kwargs)

    def Update_UI(self, *args):
        self.weather_icon.source = self.Get_Icon()

    def Get_Json_Data(self):
        result = requests.get(self.complete_url)

        json_result = result.json()

        if json_result["cod"] != "404":
            return json_result
        else:
            print("Error Code")
            return None

    # TODO: add some error checking here if some of this data does not exist
    def Get_Weather(self):
        json_data = self.Get_Json_Data()
        if json_data:
            self.location = json_data["name"]
            self.description = json_data["weather"][0]["description"]
            main = json_data["main"]
            self.temperature = main["temp"]
            self.feels_like = main["feels_like"]
            self.icon_url = self.image_prefix + json_data["weather"][0]["icon"] + self.image_suffix
            self.time_stamp = json_data["dt"]

    def Get_Temp(self):
        self.Update_Weather()
        return self.temperature
    
    def Get_Location(self):
        self.Update_Weather()
        return self.location
    
    def Get_Desc(self):
        self.Update_Weather()
        return self.description

    def Get_Feels(self):
        self.Update_Weather()
        return self.feels_like

    def Get_Icon(self):
        self.Update_Weather()
        return self.icon_url

    def Update_Weather(self):
        current_time = int(time.time())
        age = 601
        if self.time_stamp:
            age = self.time_stamp - current_time

        # If data is older than 10 mins, update the weather
        if age > 600:
            self.Get_Weather()
