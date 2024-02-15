<script lang="ts">
	import axios from "axios";
	import { onDestroy, onMount } from "svelte";
	import { BACKEND, UPDATE_VIEW_INTERVAL } from "../store";
	import { Button, Modal } from "flowbite-svelte";
	import { PlusSolid } from "flowbite-svelte-icons";

	const col_names = [
		"ID",
		"应用实例名",
		"应用实例描述",
		"应用名",
		"部署id",
		"应用消息",
		"操作"
	];
	let instances: Array<{
		pid: number,
		name: string,
		description: string,
		app_name: string,
		deploy_id: string,
		info: string
	}> = [];
	async function update() {
		const res = await axios.get(`${$BACKEND}/application/running`);
		instances = res.data;
	}
	let updater: number;
	onMount(async () => {
		updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(updater);
	});
	let to_detete: number = -1;
	let delete_modal: boolean = false;

	function delete_handle() {
		axios.delete(`${$BACKEND}/application/${to_detete}`);
		delete_modal = false;
	}
	function show_modal(pid: number) {
		to_detete = pid
		delete_modal = true;
	}
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;大模型应用</span>
	<span class="text-1xl pt-2 text-black-400 text-center"
		>&nbsp;&nbsp;展示与管理已创建的应用实例，</span
	>
</div>

<Modal title="确认删除" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要删除吗？</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					delete_handle();
				}}>删除</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

<hr class="pt-1" />
<div class="table w-full">
	<div class="w-full p-5">
		<Button href="/application/tasks"><PlusSolid size="sm" />&nbsp;&nbsp;创建应用实例</Button>
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
			{#each instances as running_app}
				<tr class="hover:bg-gray-100 rounded-lg">
					<td class="px-4 py-4">{running_app.pid}</td>
					<td class="px-4 py-4">{running_app.name}</td>
					<td class="px-4 py-4">{running_app.description}</td>
					<td class="px-4 py-4">{running_app.app_name}</td>
					<td class="px-4 py-4">
						{running_app.deploy_id}
					</td>
					<td class="px-4 py-4">
						{running_app.info}
					</td>
					<td class="px-4 py-4">
						<button class="mx-1 text-blue-600 hover:underline" on:click={(_) => {
							show_modal(running_app.pid)
						}}>
							停止并删除
						</button>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
