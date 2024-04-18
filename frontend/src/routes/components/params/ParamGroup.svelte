<script lang="ts">
  import { Hr } from "flowbite-svelte";
  import { param_component_mapper, type ParamEntry } from "./Params";

  export let entries: Array<ParamEntry>;
  export let params: any;
  export let title: string;
</script>

<div class="my-2 p-2">
  <span class="text-xl font-bold text-black m-2">{title}</span>
  <div>
    {#each entries as entry, index}
      <div class="mx-2 px-2">
        <svelte:component
          this={param_component_mapper[entry.param_type]}
          {entry}
          bind:params
        />
      </div>
      {#if index != entries.length - 1}
        <hr class="mb-1 px-4 mx-4" />
      {/if}
    {/each}
  </div>
</div>
