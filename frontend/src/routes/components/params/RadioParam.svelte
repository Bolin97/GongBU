<script lang="ts">
  import { Select, Label } from "flowbite-svelte";
  import {
    type ParamEntry,
    type MinValueConstrain,
    type MaxValueConstrain,
    type ChooseFromConstrain,
    parse_cons,
  } from "./Params";
  import { Tooltip } from 'flowbite-svelte';
  import { InfoCircleOutline } from "flowbite-svelte-icons";
  import { Radio } from "flowbite-svelte";
  import { Checkbox } from "flowbite-svelte";

  export let entry: ParamEntry;
  export let params: any;
  let value: string = params[entry.var_name];
  $: {
    params[entry.var_name] = value;
  }

  const items = parse_cons(entry.constrains).values;
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
      {#each items as item}
        <Radio class="mx-2" name="this" bind:group={value} value={item}
          >{item}</Radio
        >
      {/each}
    </div>
  </div>
</div>
