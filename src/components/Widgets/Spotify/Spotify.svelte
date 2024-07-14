<script lang="ts">
    import BaseWidget from "../BaseWidget.svelte";
    import { setUpdateCommand } from "../../../utils/timer";
    import { invoke } from "@tauri-apps/api/core";
    import { debug } from "@tauri-apps/plugin-log";
    import { onDestroy, onMount } from "svelte";
    import { authorize } from "./ApiWrapper";

    let dataSuccess: boolean = true;
    let errorMessage: string;
    let cancelCallback: () => void;

    let title: string = "Nowhere Generation";
    let artist: string = "Rise Against";
    let album: string = "Nowhere Generation";
    let albumArtUrl: string = "https://i.scdn.co/image/ab67616d00001e020abb135bc1311c23cfde51ef";
    let playing: boolean = true;
    let totalDurationMs: number = 232933;
    let elapsedMs: number = 13197;

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
    <!-- Current track -->
    <div class="flex flex-row justify-center text-center my-auto h-full">
        <!-- Track info -->
        <div class="flex flex-col justify-center m-auto">
            <div class="text-3xl p-6">{title}</div>
            <div class="text-l p-6">{artist}</div>
            <!-- Playback controls -->
            <div class="flex flex-row justify-center m-auto">
                <button class="text-5xl p-6">⏪️</button>
                <button class="text-5xl p-6">{playing ? "▶️" : "⏸️"}</button>
                <button class="text-5xl p-6">⏩️</button>
            </div>
        </div>

        <!-- Track image -->
        <img src={albumArtUrl} alt="Album art" class="rounded-3xl aspect-square">

        <!-- Progress bar -->
        <!-- <div class="flex flex-col justify-center m-auto">
            <div class="text-5xl p-6">{elapsedMs.toLocaleString(undefined, { maximumFractionDigits: 0 })}/{totalDurationMs.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
        </div> -->
    </div>
</BaseWidget>