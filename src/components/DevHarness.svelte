<script lang="ts">
    export let width = "100%";
    export let height = "100%";
</script>

<div class="flex justify-center m-auto border-4 p-2" style="width: {width}; height: {height};">
    <slot />
</div>