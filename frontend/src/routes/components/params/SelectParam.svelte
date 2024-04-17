<script lang="ts">
	import { Select, Label } from "flowbite-svelte";
	import {
		type ParamEntry,
		type MinValueConstrain,
		type MaxValueConstrain,
		type ChooseFromConstrain,
		parse_cons
	} from "./Params";

	export let entry: ParamEntry;
	export let params: any;
	let value: string = params[entry.var_name];

	$: {
		params[entry.var_name] = value;
	}

	const items = parse_cons(entry.constrains).values.map((value) => {
		return { name: value, value: value };
	});
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
			<Select {items} bind:value />
		</div>
	</div>
</div>
