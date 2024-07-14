<script lang="ts">
    import "./app.css";
    import DevHarness from "./components/DevHarness.svelte";
    import { invoke } from "@tauri-apps/api/core";
    import { type BaseWidgetType } from "./utils/layout_types";
    import { error } from "@tauri-apps/plugin-log";
    import Widget from "./Widget.svelte";
    
    let config: BaseWidgetType;

    invoke<string>("get_layout_config")
        .then(res => {
            config = JSON.parse(res)
        })
        .catch(err => {
            error(err)
        })

</script>

<main class="m-0 flex flex-col justify-center text-center h-full">
    <!-- <div class="flex justify-center mt-4">
        <DevHarness width="400px" height="250px">
            <Weather />
        </DevHarness>
    </div> -->

    <Widget backingData={config} />
</main>
