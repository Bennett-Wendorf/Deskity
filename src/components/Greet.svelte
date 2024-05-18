<script lang="ts">
  import { invoke } from "@tauri-apps/api/core"
  import { debug } from "@tauri-apps/plugin-log"

  let name = "";
  let greetMsg = ""

  async function greet(){
    // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
    greetMsg = await invoke("greet", { name })

    debug("The user has just been greeted!");
  }
</script>

<div>
  <form class="flex justify-center" on:submit|preventDefault={greet}>
    <input id="greet-input" placeholder="Enter a name..." bind:value={name} />
    <button type="submit" class="ml-2">Greet</button>
  </form>
  <p>{greetMsg}</p>
</div>