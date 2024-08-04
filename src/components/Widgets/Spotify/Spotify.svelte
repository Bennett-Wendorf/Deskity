<script lang="ts">
    import BaseWidget from "../BaseWidget.svelte";
    import { setUpdateCommand } from "../../../utils/timer";
    import { invoke } from "@tauri-apps/api/core";
    import { debug } from "@tauri-apps/plugin-log";
    import { onDestroy, onMount } from "svelte";
    import { authorize } from "./ApiWrapper";
    import { Backward, Forward, Pause, Play } from "svelte-heros-v2";
    
    let dataSuccess: boolean = true;
    let errorMessage: string;
    let cancelCallback: () => void;
    
    let title: string = "Nowhere Generation";
    let artist: string = "Rise Against";
    let album: string = "Nowhere Generation";
    let albumArtUrl: string = "https://i.scdn.co/image/ab67616d00001e020abb135bc1311c23cfde51ef";
    let playing: boolean = true;
    let totalDurationMs: number = 232933;
    let elapsedMs: number = 131197;
    
    onMount(async () => {
        let updateInterval: number = parseInt(await invoke("get_setting", { module: "spotify_widget", setting: "update_interval" }));
        let clientId: string = await invoke("get_setting", { module: "spotify_widget", setting: "client_id" });
        
        // authorize(clientId);
    });
    
    onDestroy(() => {
        cancelCallback();
    });
</script>

<BaseWidget error={!dataSuccess} errorMessage={errorMessage}>
    <div class="flex flex-col h-full w-full">
        <div class="flex flex-row justify-center text-center my-auto">
            <!-- Track info -->
            <div class="flex flex-col justify-center m-auto w-3/5 pe-2">
                <div class="text-3xl p-2 truncate">{title}</div>
                <div class="text-l p-2 truncate">{artist}</div>
                <!-- Playback controls -->
                <div class="flex flex-row justify-center m-auto">
                    <button class="py-3 px-5"><Backward variation="solid" size="50" /></button>
                    <button class="py-3 px-5">
                        {#if playing}
                            <Play variation="solid" size="50" />
                        {:else}
                            <Pause variation="solid" size="50" />
                        {/if}
                    </button>
                    <button class="py-3 px-5"><Forward variation="solid" size="50" /></button>
                </div>
            </div>
            
            <!-- Track image -->
            <div class="m-auto">
                <div class="w-full pb-full m-auto" >
                    <img src={albumArtUrl} alt="Album art" class="rounded-3xl">
                </div>
            </div>
            
        </div>
        <!-- Progress bar -->     
        <div class="w-full bg-neutral-900 rounded-full h-2.5 dark:bg-neutral-800 m-auto">
            <div class="bg-black dark:bg-gray-200 h-2.5 rounded-full" style="width: {elapsedMs/totalDurationMs * 100}%"></div>
        </div>  
    </div>
</BaseWidget>