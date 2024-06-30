<script lang="ts">
    import BaseWidget from "../BaseWidget.svelte";
    import { setUpdateCommand } from "../../../utils/timer";
    import { debug } from "@tauri-apps/plugin-log";
    import { type WeatherResponse } from "./WeatherResponse";
    import { onDestroy, onMount } from "svelte";
    import { invoke } from "@tauri-apps/api/core";

    const IMAGE_URL_PREFIX = "http://openweathermap.org/img/wn/";
    const IMAGE_URL_SUFFIX = "@4x.png";

    let temp: number = 0;
    let feelsLike: number = 0;
    let icon: string;
    let dataSuccess: boolean = true;
    let errorMessage: string;
    let cancelCallback: () => void;

    onMount(async () => {
        let updateInterval: number = parseInt(await invoke("get_setting", { module: "weather_widget", setting: "update_interval" }));

        cancelCallback = setUpdateCommand("get_weather", updateInterval * 1000, (success: boolean, response) => {
            dataSuccess = success;
            if (!success) {
                errorMessage = response;
                return;
            }

            debug(response);
            let weatherResponse: WeatherResponse = JSON.parse(response);
            temp = weatherResponse.main.temp;
            feelsLike = weatherResponse.main.feels_like;
            icon = weatherResponse.weather[0].icon;
        })
    });

    onDestroy(() => {
        cancelCallback();
    });
</script>

<BaseWidget error={!dataSuccess} errorMessage={errorMessage}>
    <div class="flex flex-row justify-center text-center my-auto h-full">
        <img src="{IMAGE_URL_PREFIX + (icon ?? "02d") + IMAGE_URL_SUFFIX}" alt="Temp weather info" class="h-24 m-auto">

        <div class="flex flex-col justify-center m-auto">
            <div class="text-5xl p-6">{temp.toLocaleString(undefined, { maximumFractionDigits: 0 })}°F</div>
            <div class="text-xl p-6">Feels like: {feelsLike.toLocaleString(undefined, { maximumFractionDigits: 0 })}°F</div>
        </div>
    </div>
</BaseWidget>