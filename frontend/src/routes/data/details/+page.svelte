<script lang="ts">
	import { Label, Radio, Button, Hr, Modal } from "flowbite-svelte";
	import { AngleLeftSolid } from "flowbite-svelte-icons";
	import { page } from "$app/stores";
	import Uploader from "../Uploader.svelte";
	import { goto } from "$app/navigation";
	import axios from "axios";
	import { BACKEND } from "../../store";

	const id = $page.url.searchParams.get("pool_id");

	let next_modal = false;
	let delete_modal = false
	let stage_empty: boolean;

	async function handle_delete() {
		await axios.delete(`${$BACKEND}/pool/${id}`);
		goto(`/data`);
	}

	function return_handle() {
		if (stage_empty) {
			goto(`/data`);
		} else {
			next_modal = true;
		}
	}
</script>

<Modal title="确认删除吗" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
		确认要删除吗？
	</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		数据将<span class="font-semibold">无法</span>恢复。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					handle_delete()
				}}>是的</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

<Modal title="暂存区中仍有未提交的数据" bind:open={next_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
		确认要返回吗？暂存区中仍有未提交的数据。
	</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		暂存区的数据将<span class="font-semibold">不会</span>被保存。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					goto(`/data/details?pool_id=${id}`);
				}}>是的</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>
<div>
	<div class="flex flex-row justify-between">
		<div class="flex">
			<div class="flex flex-row">
				<Button
					on:click={(_) => {
						return_handle();
					}}
				>
					<AngleLeftSolid size="sm" />返回
				</Button>
			</div>
			<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;数据池详情</span>
		</div>
		<div class="flex flex-row">
			<Button
				on:click={(_) => {
					delete_modal = true;
				}}
				color="red"
			>
				删除此数据池
			</Button>
		</div>
	</div>
	<Hr />
	<Uploader bind:stageEmpty={stage_empty} poolId={Number.parseInt(id)} />
</div>
