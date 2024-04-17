<script lang="ts">
	import {
		Modal,
		Button,
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell
	} from "flowbite-svelte";
	import type FinetuneDatasetEntry from "../../class/DatasetEntry";
	import axios from "axios";
	const col_names = ["id", "名称", "创建时间", "数据量", "格式", "描述"];

	export let datasetEntries: Array<FinetuneDatasetEntry>;
	let delete_modal = false;
	let id_to_delete: null | number = null;

	import { createEventDispatcher } from "svelte";

	const dispatch = createEventDispatcher();

	async function delete_handle() {
		if (id_to_delete == null) {
			throw "Attempting to delete without an id";
		}
		await axios.delete(`/api/dataset/${id_to_delete}`);
		dispatch("modified");
	}
</script>

<Modal title="确认删除" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
		确认要删除这个数据集吗？
	</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">删除后数据将不可恢复。</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button color="red" on:click={() => delete_handle()}>删除</Button>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

<Table striped={true}>
	<TableHead>
		{#each col_names as name}
			<TableHeadCell>{name}</TableHeadCell>
		{/each}
	</TableHead>
	<TableBody>
		{#each datasetEntries as row}
			<TableBodyRow>
				<TableBodyCell>{row.id}</TableBodyCell>
				<TableBodyCell>{row.name}</TableBodyCell>
				<TableBodyCell>{row.created_on}</TableBodyCell>
				<TableBodyCell>{row.size}</TableBodyCell>
				<TableBodyCell>{row.type}</TableBodyCell>
				<TableBodyCell>{row.description}</TableBodyCell>
				<TableBodyCell>
					<button
						class="text-blue-500 hover:underline hover:text-blue-700"
						on:click={(_) => {
							id_to_delete = row.id;
							delete_modal = true;
						}}>删除数据</button
					>
				</TableBodyCell>
			</TableBodyRow>
		{/each}
	</TableBody>
</Table>

{#if datasetEntries.length == 0}
	<div class="w-full text-center">
		<span>数据池中无数据集</span>
	</div>
{/if}
