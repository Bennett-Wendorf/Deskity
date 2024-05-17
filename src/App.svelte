<script lang="ts">
    import "./app.css";
    import DevHarness from "./components/DevHarness.svelte";
    import Greet from "./components/Greet.svelte";
    import Weather from "./components/Widgets/Weather/Weather.svelte";
</script>

<main class="m-0 pt-[10vh] flex flex-col justify-center text-center">
    <h1 class="align-center">Welcome to Tauri!</h1>

    <div class="flex justify-center">
        <a href="https://vitejs.dev" target="_blank" class="font-medium">
            <img src="/vite.svg" class="h-24 p-6 will-change-[filter] duration-700 vite" alt="Vite Logo" />
        </a>
        <a href="https://tauri.app" target="_blank" class="font-medium">
            <img src="/tauri.svg" class="h-24 p-6 will-change-[filter] duration-700 tauri" alt="Tauri Logo" />
        </a>
        <a href="https://svelte.dev" target="_blank" class="font-medium">
            <img src="/svelte.svg" class="h-24 p-6 will-change-[filter] duration-700 svelte" alt="Svelte Logo" />
        </a>
    </div>

    <p>Click on the Tauri, Vite, and Svelte logos to learn more.</p>

    <div class="flex justify-center">
        <Greet></Greet>
    </div>

    <div class="flex justify-center mt-4">
        <DevHarness width="400px" height="250px">
            <Weather />
        </DevHarness>
    </div>
</main>
