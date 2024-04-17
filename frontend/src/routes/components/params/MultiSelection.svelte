<script lang="ts">
	import { Select, Label } from "flowbite-svelte";
	import {
		type ParamEntry,
		type MinValueConstrain,
		type MaxValueConstrain,
		type ChooseFromConstrain,
		parse_cons
	} from "./Params";
	import { Radio } from "flowbite-svelte";
	import { Checkbox } from 'flowbite-svelte';

	export let entry: ParamEntry;
	export let params: any;
	let value: Array<any> = params[entry.var_name];
    $: params[entry.var_name] = value
	const items = parse_cons(entry.constrains).values;
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
			{#each items as item (item)}
                <Checkbox class="mx-2" value={item} checked={value.includes(item)} on:change={
					(_) => {
						if (value.includes(item)) {
							value = value.filter((each) => each != item);
						} else {
							value = [...value, item];
						}
					}
				}>{item}</Checkbox>
            {/each}
		</div>
	</div>
</div>
