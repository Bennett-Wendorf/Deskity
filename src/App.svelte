<script lang="ts">
    import "./app.css";
    import DevHarness from "./components/DevHarness.svelte";
    import Greet from "./components/Greet.svelte";
    import Weather from "./components/Widgets/Weather/Weather.svelte";
    import FrontendWeather from "./components/Widgets/FrontendOnlyWeather/Weather.svelte";
    import HorizontalSplit from "./components/Layout/HorizontalSplit.svelte";
    import VerticalSplit from "./components/Layout/VerticalSplit.svelte";
</script>

<main class="m-0 py-[10vh] flex flex-col justify-center text-center">
    <div class="flex justify-center mt-4">
        <DevHarness width="400px" height="250px">
            <FrontendWeather />
        </DevHarness>
        <DevHarness width="400px" height="250px">
            <Weather />
        </DevHarness>
    </div>

    <div>
        <DevHarness width="1024px" height="600px">
            <HorizontalSplit>
                <VerticalSplit slot="left">
                    <HorizontalSplit slot="left">
                        <Weather slot="left" />
                        <Weather slot="right" />
                    </HorizontalSplit>
                    <Weather slot="right" />
                </VerticalSplit>
                <FrontendWeather slot="right" />
            </HorizontalSplit>
        </DevHarness>
    </div>
</main>
