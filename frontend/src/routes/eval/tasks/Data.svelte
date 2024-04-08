<script lang="ts">
	import axios from "axios";
	import { Select, Label } from "flowbite-svelte";
	import { onMount } from "svelte";
	import type PoolEntry from "../../../class/PoolEntry";
	import type DatasetEntry from "../../../class/DatasetEntry";

	interface ValueNamePair {
		value: string;
		name: string;
	}

	let selectedPool: string;
	export let selectedSet: string;

	let pool_options = [] as Array<ValueNamePair>;
	onMount(async () => {
		const pools = (await axios.get(`/api/pool/`)).data as Array<PoolEntry>;
		pool_options = pools.map((entry) => {
			return {
				value: entry.id.toString(),
				name: entry.name
			};
		});
	});
	let sets = [] as Array<ValueNamePair>;
	let loading = false;
	$: {
		if (selectedPool) {
			loading = true;
			axios.get(`/api/dataset_entry/by_pool/${selectedPool}`).then((res) => {
				sets = (res.data as Array<DatasetEntry>).map((entry) => {
					return {
						value: entry.id.toString(),
						name: entry.name
					};
				});
				loading = false;
			});
		}
	}
</script>

<div class="m-4">
	<div class="m-4 my-8">
		<Label>
			选择数据池：
			<Select
				class="mt-2"
				items={pool_options}
				bind:value={selectedPool}
				placeholder="选择数据池"
			/>
		</Label>
	</div>
	<div class={`m-4 my-8 ${loading ? "hidden" : ""}`}>
		<Label>
			选择数据集：
			<Select class="mt-2" items={sets} bind:value={selectedSet} placeholder="选择数据集" />
		</Label>
	</div>
</div>
