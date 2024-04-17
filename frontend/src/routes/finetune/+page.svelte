<script lang="ts">
	import { Button } from "flowbite-svelte";
	import type FinetuneEntry from "../../class/FinetuneEntry";
	import { onDestroy, onMount } from "svelte";
	import axios from "axios";
	import { PlusOutline } from "flowbite-svelte-icons";
	import { UPDATE_VIEW_INTERVAL } from "../store";
	import FinetuneProgess from "./FinetuneProgess.svelte";
	import { page } from "$app/stores";
	import toFormatted from "../../utils/ConvertDatetimeString";
	import type FinetuneEntryReduced from "../../class/FinetuneEntryReduced";
    import FinetuneCard from "./FinetuneCard.svelte";
    import ActionPageTitle from "../components/ActionPageTitle.svelte";

	const col_names = ["ID", "名称", "创建时间", "进度", "状态", "描述", ""];

	let entries = [] as Array<FinetuneEntryReduced>;

	let entries_updater: any;
	onMount(async () => {
		async function update() {
			entries = (await axios.get(`/api/finetune_entry/reduced`))
				.data as Array<FinetuneEntryReduced>;
		}
		update();
		entries_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(entries_updater);
	});
</script>

<ActionPageTitle title="微调管理" subtitle="微调">
	<svelte:fragment slot="right">
		<Button href="/finetune/tasks">
			<PlusOutline />
			创建微调任务
		</Button>
	</svelte:fragment>
</ActionPageTitle>

<hr class="pt-1" />
<div class="grid grid-cols-3">
	{#each entries as entry}
		<div class="mx-4 my-2">
			<FinetuneCard entry={entry}/>
		</div>
	{/each}
</div>
