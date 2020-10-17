import requests
import json
import time

class Weather():
    api_key = "bbd4a506dfb2384cf85c057a674e92fb"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    image_prefix = "http://openweathermap.org/img/wn/"
    image_suffix = "@2x.png"

    units = "imperial"

    def __init__(self):
        # This will need to be set somehow, probably in configuration files
        self.city_name = "Stevens Point"

        self.complete_url = self.base_url + "appid=" + self.api_key + "&q=" + self.city_name + "&units=" + self.units

        self.Get_Weather()

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
        print(json_data)
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