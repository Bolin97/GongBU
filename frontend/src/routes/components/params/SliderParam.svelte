<script lang="ts">
  import { Button, Label } from "flowbite-svelte";
  import {
    type ParamEntry,
    type MinValueConstrain,
    type MaxValueConstrain,
    type StepConstrain,
    type ChooseFromConstrain,
    parse_cons,
  } from "./Params";

  export let entry: ParamEntry;
  export let params: any;
  let value: number = params[entry.var_name];

  const { max, min, step, values } = parse_cons(entry.constrains);

  // const m_precision = Math.max(
  // 		...([max, min].map((num) => {
  // 			const str = num.toString();
  // 			const decimalPos = str.indexOf('.');
  // 			return decimalPos === -1 ? 0 : str.length - decimalPos - 1;
  // 		}))
  // 	)
  // const precision =
  //     m_precision == 0 ? 0 : m_precision + 2;

  function check_value() {
    value = value > max ? max : value;
    value = value < min ? min : value;
  }

  $: {
    params[entry.var_name] = value;
  }
</script>

<div class="p-2 w-full">
  <div class="flex flex-row w-full justify-between">
    <div>
      <div class="mb-2 text-base text-black">
        {entry.name}
      </div>

      <div class="text-gray-600 mb-2 text-sm">
        {entry.description}
      </div>
    </div>

    <div class="m-2 p-2 flex items-center">
      <div class="relative w-full mx-2">
        <input
          type="range"
          bind:value
          {min}
          {max}
          {step}
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
        />
        <span
          class="text-sm text-gray-500 dark:text-gray-400 absolute start-0 -bottom-6"
          >{min}</span
        >
        <span
          class="text-sm text-gray-500 dark:text-gray-400 absolute end-0 -bottom-6"
          >{max}</span
        >
      </div>
      <div class="mx-2">
        <input
          type="number"
          aria-describedby="helper-text-explanation"
          class={`bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
          bind:value
          {step}
          on:focusout={(_) => check_value()}
        />
      </div>
    </div>
  </div>

  <div class="my-1 w-full flex flex-row justify-end">
    {#if values.length > 0}
      <div>
        <span class="mr-2 text-gray-600">推荐值：</span>
        {#each values as preset}
          <button
            class="mx-2 py-2 w-16 text-center rounded border border-gray-200 hover:border-blue-600"
            on:click={(_) => {
              value = Number.parseFloat(preset.toString());
            }}>{preset}</button
          >
        {/each}
      </div>
    {/if}
  </div>
</div>
