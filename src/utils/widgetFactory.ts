import Weather from "../components/Widgets/Weather/Weather.svelte";
import FrontendWeather from "../components/Widgets/FrontendOnlyWeather/Weather.svelte";

let widgetsMap = new Map<string, typeof Weather>([
    ["weather", Weather],
    ["frontendweather", FrontendWeather]
]);

export function getWidget(type: string): any {
    return widgetsMap.get(type);
}