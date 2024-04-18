<script lang="ts">
  import { Label, Input } from "flowbite-svelte";
  import ServerFile from "./ServerFile.svelte";

  export let dirArr: Array<string> = [];
</script>

<div>
  <div class="text-2xl m-2 my-4">
    <Label for="output" class="mb-2">输出路径</Label>
  </div>

  <div class="m-4 rounded p-2">
    <ServerFile bind:dir={dirArr} />
  </div>
</div>
