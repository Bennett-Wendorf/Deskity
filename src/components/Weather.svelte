<script lang="ts">
    import Widget from "./Widget.svelte";


</script>

<Widget>
    <div class="flex flex-row justify-center text-center my-auto h-full">
        <img src="/tauri.svg" alt="Temp weather info" class="h-24 p-4 m-auto">
    
        <div class="flex flex-col justify-center m-auto">
            <div class="text-5xl p-6">72°F</div>
            <div class="text-xl p-6">Feels like: 68°F</div>
        </div>
    </div>
</Widget>