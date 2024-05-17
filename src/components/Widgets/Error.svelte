<script lang="ts">
    export let errorText: string = "Something went wrong!";
</script>

<div class="text-red-500 text-2xl flex flex-col justify-center h-full">
    <p>{errorText}</p>
</div>