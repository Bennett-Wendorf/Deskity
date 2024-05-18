<script lang="ts">
    import Error from "./Error.svelte";

    export let error: boolean = false;

    export let errorMessage: string = "";
</script>

<div class="w-full m-2 border rounded-3xl border-neutral-700 bg-neutral-700 p-4 text-white">
    {#if error}
        <slot name="error">
            {#if errorMessage}
                <Error errorText={errorMessage} />
            {:else}
                <Error />
            {/if}
        </slot>
    {:else}
        <slot />
    {/if}
</div>