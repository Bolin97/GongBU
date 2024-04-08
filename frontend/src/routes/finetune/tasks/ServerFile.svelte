<!-- src/routes/filesystem.svelte -->
<script lang="ts">
	import { onDestroy, onMount } from "svelte";
	import { goto } from "$app/navigation";
	import { FileOutline, FolderOutline } from "flowbite-svelte-icons";
	import { Button, Input, Label, Modal } from "flowbite-svelte";
	import axios from "axios";
	import { DEFAULT_MODEL_OUTPUT, UPDATE_VIEW_INTERVAL } from "../../store";

	type FileEntry = {
		name: string;
		isDirectory: boolean;
	};

	let files: Array<FileEntry> = [];
	export let dir: Array<string> = $DEFAULT_MODEL_OUTPUT.split("/").filter((x) => x != "");

	onMount(load);

	let loading = false;
	async function load() {
		const res = (
			await axios.get(
				`/api/file`, {
					params: {
						dir: encodeURIComponent("/" + dir.join("/"))
					}
				}
			)
		).data;
		if (res.failure) {
			dir = dir.filter((_, ind) => ind != dir.length - 1);
			alert("访问出错！");
		}
		files = res;
	}

	function navigate(file: FileEntry) {
		if (file.isDirectory) {
			loading = true;
			dir = [...dir, file.name];
			load();
			loading = false;
		} else {
			// handle file click
		}
	}

	function go_back() {
		loading = true;
		dir = dir.filter((_, ind) => ind != dir.length - 1);
		load();
		loading = false;
	}

	async function new_folder() {
		axios.post(
			`/api/file`, {}, {
				params: {
					dir: encodeURIComponent("/" + dir.join("/")),
					new: new_folder_name,
				}
			}
		);
		new_folder_name = "";
		setTimeout(load, UPDATE_VIEW_INTERVAL);
	}

	// let new_folder_updater: number;
	// onMount(() => {
	// 	new_folder_updater = setInterval(load, UPDATE_VIEW_INTERVAL);
	// });
	// onDestroy(() => {
	// 	clearInterval(new_folder_updater);
	// });

	let new_folder_modal = false;
	let new_folder_name = "";
</script>

<Modal title="新建文件夹" bind:open={new_folder_modal} autoclose outsideclose>
	<Label>
		输入新文件夹名：
		<Input class="m-2 p-2" placeholder="新文件夹名" bind:value={new_folder_name} />
	</Label>
	<svelte:fragment slot="footer">
		<div class="gap-2 w-full flex justify-end">
			<Button disabled={new_folder_name.length == 0} on:click={() => new_folder()}
				>创建</Button
			>
			<Button color="alternative">取消</Button>
		</div>
	</svelte:fragment>
</Modal>

<div class="flex flex-row gap-2">
	<Button
		class={`my-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${loading ? "transition ease-in-out opacity-50 disabled" : ""}`}
		on:click={(_) => go_back()}
		disabled={dir.length === 0}
	>
		<svg class="w-4 h-4 mr-1 text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 8 14">
			<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 1 1.3 6.326a.91.91 0 0 0 0 1.348L7 13"/>
		</svg>
		返回上级
	</Button>
	<Button
		class={`my-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${loading ? "transition ease-in-out opacity-50 disabled" : ""}`}
		on:click={(_) => load()}
	>
		<svg class="w-4 h-4 text-white mr-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 20">
			<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 1v5h-5M2 19v-5h5m10-4a8 8 0 0 1-14.947 3.97M1 10a8 8 0 0 1 14.947-3.97"/>
		</svg>
		刷新
	</Button>
	<Button
	class={`my-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${loading ? "transition ease-in-out opacity-50 disabled" : ""}`}
		on:click={(_) => (new_folder_modal = true)}
	>
		<svg class="w-4 h-4 text-white mr-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 18">
			<path d="M9.043.8a2.009 2.009 0 0 0-1.6-.8H2a2 2 0 0 0-2 2v2h11.443L9.043.8ZM0 6v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6H0Zm11 7h-1v1a1 1 0 1 1-2 0v-1H7a1 1 0 0 1 0-2h1v-1a1 1 0 0 1 2 0v1h1a1 1 0 0 1 0 2Z"/>
		</svg>
		新建文件夹
	</Button>
	<div class="align-middle m-2 flow-root text-gray-800">
		当前路径：
		<div>{"/" + dir.join("/")}</div>
	</div>
</div>

<div class={`${loading ? "transition ease-in-out opacity-50" : ""} overflow-y-scroll max-h-[53vh]`}>
	{#each files as file (file.name)}
		<div class="inline-grid mx-4 my-1">
			<button
				disabled={loading}
				class="flex flex-row items-center space-x-2 p-2 rounded hover:bg-gray-200"
				on:click={(_) => navigate(file)}
			>
				{#if file.isDirectory}
					<FolderOutline class="text-blue-500" />
				{:else}
					<FileOutline class="text-gray-500" />
				{/if}
				<p class="text-gray-700">{file.name}</p>
			</button>
		</div>
	{/each}
</div>
