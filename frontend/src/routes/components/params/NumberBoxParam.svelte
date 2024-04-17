<script lang="ts">
	import { Button, Label } from "flowbite-svelte";
	import {
		type ParamEntry,
		type MinValueConstrain,
		type MaxValueConstrain,
		parse_cons
	} from "./Params";
	import { each } from "svelte/internal";

	export let entry: ParamEntry;
	export let params: any;
	let value: number = params[entry.var_name];

	const { max, min, step, values } = parse_cons(entry.constrains);

	const change_by = [1, 2, 5, 10, 100];

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

		<div class="flex flex-row m-2 p-2">
			<input
				type="number"
				aria-describedby="helper-text-explanation"
				class={`bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
				bind:value
				on:focusout={(_) => check_value()}
			/>
		</div>
	</div>

	<div class="my-1 w-full flex flex-row justify-end">
		{#if values.length > 0}
			<div>
				<span class="mr-2 text-gray-600">推荐值：</span>
				{#each values as preset}
					<button
						class="mx-2 py-2 w-16 text-center rounded border border-gray-200 hover:border-blue-600"
						on:click={(_) => (value = Number.parseInt(preset.toString()))}
						>{preset}</button
					>
				{/each}
			</div>
		{/if}
	</div>
</div>
