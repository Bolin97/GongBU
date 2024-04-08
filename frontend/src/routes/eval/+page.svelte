<script lang="ts">
	import { Button } from "flowbite-svelte";
	import { PlusOutline } from "flowbite-svelte-icons";
	import type FinetuneEntry from "../../class/FinetuneEntry";
	import { onDestroy, onMount } from "svelte";
	import axios from "axios";
	import { UPDATE_VIEW_INTERVAL } from "../store";
	import { page } from "$app/stores";
	import toFormatted from "../../utils/ConvertDatetimeString";
	import type FinetuneEntryReduced from "../../class/FinetuneEntryReduced";

	const col_names = ["ID", "名称", "创建时间", "进度", "状态", "描述", ""];

	let entries = [] as Array<FinetuneEntryReduced>;

	let entries_updater: number;

	onMount(async () => {
		async function update() {
			entries = (await axios.get(`api/finetune_entry/reduced`))
				.data as Array<FinetuneEntryReduced>;
		}
		update();
		entries_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(entries_updater);
	});
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;模型评估</span>
	<span class="text-1xl pt-2 text-black-400 text-center"
		>&nbsp;&nbsp;对基模型或微调模型进行评估</span
	>
</div>
<hr class="pt-1" />

<div class="table w-full">
	<div class="w-full p-5">
		<Button href="/eval/tasks"><PlusOutline size="sm" />&nbsp;&nbsp;创建评估任务</Button>
	</div>
	<table class="table-auto border-collapse w-full h-full">
		<thead>
			<tr
				class="rounded-lg text-sm font-medium text-gray-700 text-left"
				style="font-size: 0.9674rem"
			>
				{#each col_names as name (name)}
					<th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">{name}</th>
				{/each}
			</tr>
		</thead>
		<tbody class="text-sm font-normal text-gray-700">
			{#each entries as entry}
				<tr class="hover:bg-gray-100 rounded-lg">
					<td class="px-4 py-4">{entry.id}</td>
					<td class="px-4 py-4">{entry.name}</td>
					<td class="px-4 py-4">{toFormatted(entry.start_time)}</td>
					<td class="px-4 py-4 w-40">
						{#if entry.state == -1}
							<div class="text-2xl font-bold">-</div>
						{:else}
							<!-- <FinetuneProgess id={entry.id} noUpdate={entry.state == 1}/> -->
						{/if}
					</td>
					<td class="px-4 py-4">
						{#if entry.state == 0}
							训练中
						{:else if entry.state == 1}
							训练完成
						{:else if entry.state == -1}
							出错
						{:else}
							无效状态码
						{/if}
					</td>
					<td class="px-4 py-4">{entry.description}</td>
					<td class="px-4 py-4">
						<a
							href={`/finetune/details?finetune_id=${entry.id}`}
							class="text-blue-600 hover:underline"
						>
							详细信息
						</a>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>