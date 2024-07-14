import Weather from "../components/Widgets/Weather/Weather.svelte";
import FrontendWeather from "../components/Widgets/FrontendOnlyWeather/Weather.svelte";
import Spotify from "../components/Widgets/Spotify/Spotify.svelte";

let widgetsMap = new Map<string, typeof Weather>([
    ["weather", Weather],
    ["frontendweather", FrontendWeather],
    ["spotify", Spotify]
]);

export function getWidget(type: string): any {
    return widgetsMap.get(type);
}