import requests
import json
from datetime import datetime
import threading
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

        super(WeatherWidget, self).__init__(**kwargs)

        # TODO Add this interval to a config
        update_interval = 600 # seconds
        Clock.schedule_interval(self.Start_Update_Loop, update_interval)

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
        print(f"[Weather Widget] [{self.Get_Timestamp()}] Pulling weather data")
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

    # TODO Add this to a helper class for use accross integrations
    def Get_Timestamp(self):
        '''
        Return the current timestamp in the format that is used for all output for this program.
        '''
        return datetime.now().strftime("%m/%d/%y %H:%M:%S.%f")[:-4]