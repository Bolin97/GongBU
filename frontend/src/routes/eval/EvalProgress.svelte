<script lang="ts">
  import { Progressbar } from "flowbite-svelte";
  import { onDestroy, onMount } from "svelte";
  import { UPDATE_VIEW_INTERVAL } from "../store";
  import axios from "axios";
  export let id: string;
  export let noUpdate = false;
  let percentage = "0";
  /**
     * {
  "entry_id": 8,
  "id": 8,
  "current": 6,
  "total": 17
}
    */
  interface FinetuneProgessEntry {
    entry_id: number;
    id: number;
    current: number;
    total: number;
  }
  let entry: FinetuneProgessEntry = undefined;
  let percentage_updater: any;
  onMount(async () => {
    async function update() {
      entry = (await axios.get(`/api/eval/progress/${id}`))
        .data as FinetuneProgessEntry;
      if (entry.current == entry.total) {
        clearInterval(percentage_updater);
      }
      percentage = ((entry.current * 100) / entry.total).toFixed(1);
    }
    update();
    if (!noUpdate) {
      percentage_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
    }
  });
  onDestroy(() => {
    clearInterval(percentage_updater);
  });
</script>

{#if entry != undefined && entry != null}
  <div class="w-full h-4 bg-gray-400 rounded dark:bg-gray-700">
    {#if Number.parseFloat(percentage) >= 0.05}
      <div
        class="bg-blue-600 text-xs font-medium text-white text-center p-0.5 leading-none rounded"
        style="width: {percentage}%"
      >
        {percentage}%
      </div>
    {:else}
      <div
        class="text-xs font-medium text-white text-center p-0.5 leading-none rounded"
        style="width: {percentage}%"
      >
        {percentage}%
      </div>
    {/if}
    {#if entry != undefined && entry.total > 1}
      <div class="w-full text-center items-center text-sm">
        <span>{entry.current}</span> <span class="mx-1">/</span><span>
          {entry.total}</span
        >
      </div>
    {/if}
  </div>
{/if}
