<script lang="ts">
  import { Button, Checkbox, Label } from "flowbite-svelte";
  import type {
    ParamEntry,
    MinValueConstrain,
    MaxValueConstrain,
  } from "./Params";
  import { Tooltip } from 'flowbite-svelte';
  import { InfoCircleOutline } from "flowbite-svelte-icons";

  export let entry: ParamEntry;
  export let params: any;

  let value = params[entry.var_name];

  $: {
    params[entry.var_name] = value;
  }
</script>

<div class="p-2 w-full">
  <div class="flex flex-row w-full justify-between">
    <div class="flex flex-row">
      <div class="mb-2 text-base text-black">
        {entry.name}
      </div>
      <div class="m-1">
        <InfoCircleOutline
          id={entry.var_name}
          size="sm"
          class="text-primary-500 dark:text-primary-400"
        />
        <Tooltip triggeredBy="#{entry.var_name}">{entry.description}</Tooltip>
      </div>
    </div>

    <div class="flex flex-row m-2 p-2">
      <label class="flex items-center cursor-pointer">
        <input type="checkbox" class="hidden" bind:checked={value} />
        <span
          class={`cursor-pointer h-6 w-6 border border-gray-300 rounded-md flex items-center justify-center ${
            value ? "bg-blue-500" : "bg-white"
          }`}
        >
          {#if value}
            <svg
              class="h-4 w-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          {/if}
        </span>
      </label>
    </div>
  </div>
</div>
