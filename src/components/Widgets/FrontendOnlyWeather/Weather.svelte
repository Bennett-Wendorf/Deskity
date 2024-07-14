<script lang="ts">
    import BaseWidget from "../BaseWidget.svelte";
    import { setUpdateCommand } from "../../../utils/timer";
    import { type WeatherResponse } from "./WeatherResponse";
    import { onDestroy, onMount } from "svelte";
    import { invoke } from "@tauri-apps/api/core";
    import { debug } from "@tauri-apps/plugin-log";

    const IMAGE_URL_PREFIX = "http://openweathermap.org/img/wn/";
    const IMAGE_URL_SUFFIX = "@4x.png";

    let apiKey: string;
    let city: string;
    let units: string;
    let temp: number = 0;
    let feelsLike: number = 0;
    let icon: string;
    let dataSuccess: boolean = true;
    let errorMessage: string;
    let cancelCallback: () => void;

    async function getWeather() {
        let response = await fetch(`http://api.openweathermap.org/data/2.5/weather?appid=${apiKey}&q=${city}&units=${units}`);
        
        if (response.ok) {
            debug(`${response.json()}`);
            return response.json();
        } else {
            dataSuccess = false;
            errorMessage = response.statusText;
            return {};
        }
    }

    function responseIsString(response: WeatherResponse | string): response is string {
        return typeof response === "string";
    }

    onMount(async () => {
        let updateInterval: number = parseInt(await invoke("get_setting", { module: "weather_widget", setting: "update_interval" }));
        [apiKey, city, units] = await Promise.all([
            invoke<string>("get_setting", { module: "weather_widget", setting: "api_key" }),
            invoke<string>("get_setting", { module: "weather_widget", setting: "city_name" }),
            invoke<string>("get_setting", { module: "weather_widget", setting: "units" })
        ]);

        cancelCallback = setUpdateCommand(getWeather, updateInterval * 1000, (success: boolean, response: WeatherResponse | string) => {
            dataSuccess = success;
            if (!success && responseIsString(response)) {
                errorMessage = response;
                return;
            }

            if (!responseIsString(response)) {
                temp = response.main.temp;
                feelsLike = response.main.feels_like;
                icon = response.weather[0].icon;
            }
        });
    });

    onDestroy(() => {
        cancelCallback();
    });
</script>

<BaseWidget error={!dataSuccess} errorMessage={errorMessage}>
    <div class="flex flex-row justify-center text-center my-auto h-full">
        <img src="{IMAGE_URL_PREFIX + (icon ?? "02d") + IMAGE_URL_SUFFIX}" alt="Temp weather info" class="h-24 m-auto">

        <div class="flex flex-col justify-center m-auto">
            <div class="text-5xl p-6">{temp.toLocaleString(undefined, { maximumFractionDigits: 0 })}°C</div>
            <div class="text-xl p-6">Feels like: {feelsLike.toLocaleString(undefined, { maximumFractionDigits: 0 })}°F</div>
        </div>
    </div>
</BaseWidget>