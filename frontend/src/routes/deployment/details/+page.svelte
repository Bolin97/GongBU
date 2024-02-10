<script lang="ts">
	import { Button, Hr, Label, Tooltip, A, Progressbar, Modal } from "flowbite-svelte";
	import { AngleLeftSolid } from "flowbite-svelte-icons";
	import Chart from "../../../components/Chart.svelte";
	import { page } from "$app/stores";
	import { onMount, onDestroy } from "svelte"
	import axios from "axios";
	import { BACKEND, LIST_SPLITTER, UPDATE_VIEW_INTERVAL } from "../../store";
	import type FinetuneEntry from "../../../class/FinetuneEntry";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	import type CudaDeviceEntry from "../../../class/CudaDeviceEntry";
	import { goto } from "$app/navigation";

	enum DeploymentState {
		"出错" = -1,
		"准备中" = 0,
		"等待中" = 1,
		"可用" = 2,
		"停止" = 3,
	}

	function color_map(state: number) {
		switch(state) {
			case -1:
				return "red";
			case 0:
				return "yellow";
			case 1:
				return "blue";
			case 2:
				return "green";
			case 3:
				return "alternative";
			default:
				return "primary";
		}
	}
	 

	const id = $page.url.searchParams.get("entry_id") as string;
	let entry: DeploymentEntry = {
		entry_id: 0,
		name: "",
		start_time: "",
		end_time: "",
		state: 0,
		description: "",
		model_or_finetune_id: 0,
		deploy_finetuned: false,
		port: 0,
		devices: "auto",
		params: {},
	};
	$: running = entry.state == 2;
	let openllm_entry: OpenllmEntry;
	let devices: Array<CudaDeviceEntry> = [];
	let devices_updater: string | number | NodeJS.Timeout;
	onMount(async () => {
		async function update() {
			devices = (await axios.get(`${$BACKEND}/cuda/`)).data as Array<CudaDeviceEntry>;
		}
		devices = (await axios.get(`${$BACKEND}/cuda/`)).data as Array<CudaDeviceEntry>;
		devices_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(async() => {
		clearInterval(devices_updater);
	})
	let state_update: string | number | NodeJS.Timeout;
	onMount(async () => {
		async function update() {
			entry.state = (await axios.get(`${$BACKEND}/deploy_entry/state/${id}`)).data as number;
		}
		state_update = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(async () => {
		clearInterval(state_update);
	});

	let access_data: Array<{date: Date, count: number}> = [];
	onMount(async() => {
		access_data = (await axios.get(`${$BACKEND}/access_counter/${id}`)).data as Array<{date: Date, count: number}>;
	});
	$: access_chart = {
		chart: {
			type: "line"
		},
		xaxis: {
			type: "datetime",
		},
		stroke: {
			curve: 'straight',
			width: [2, 2, 2]
		},
		series: [
			{
				name: "times",
				data: access_data.map((each) => {
					return {
						x: each.date,
						y: each.count
					}
				})
			}
		]
	};

	let deployed_on: Array<number> | "auto" = [];
	onMount(async () => {
		entry = (await axios.get(`${$BACKEND}/deploy_entry/${id}`)).data as DeploymentEntry;
		
		if(entry.deploy_finetuned) {
			const finetune_entry: FinetuneEntry = (await axios.get(`${$BACKEND}/finetune_entry/${entry.model_or_finetune_id}`)).data as FinetuneEntry;
			openllm_entry = (await axios.get(`${$BACKEND}/openllm/${finetune_entry.model_id}`)).data as OpenllmEntry;
		}
		else {
			openllm_entry = (await axios.get(`${$BACKEND}/openllm/${entry.model_or_finetune_id}`)).data as OpenllmEntry;
		}
		const devices_strings = entry.devices.split(LIST_SPLITTER);
		if(devices_strings.length == 1 && devices_strings[0] == "auto") {
			deployed_on = "auto";
		}
		else {
			deployed_on = devices_strings.map((value) => parseInt(value));
		}
	});

	let stop_modal = false;
	async function stop() {
		await axios.put(`${$BACKEND}/deploy/stop/${id}`);
	}

	let delete_modal = false;
	async function delete_entry() {
		await axios.delete(`${$BACKEND}/deploy_entry/${id}`);
		goto("/deployment");
	}

	async function start() {
		await axios.put(`${$BACKEND}/deploy/${id}`);
	}
</script>

<Modal title="确认停止" bind:open={stop_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要停止模型部署吗？</p>
	<p class="text-base leading-relaxed text-green-600 dark:text-gray-400">
		您可以在之后重启此任务。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="blue"
				on:click={() => {
					stop();
				}}>是的</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

<Modal title="确认删除" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要删吃此部署任务吗？</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		此操作无法撤销。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					delete_entry();
				}}>是的</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

{#if openllm_entry != undefined}
<div>
	<div class="flex flex-row justify-between">
		<div class="flex">
			<div class="">
				<Button href="/deployment">
					<AngleLeftSolid size="sm" />返回
				</Button>
			</div>
			<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;详细信息</span>
		</div>
		<div class="flex gap-2">
			{#if running}
				<Button color="blue" on:click={(_) => { stop_modal = true; }}>停止</Button>
			{/if}
			{#if !running}
				<Button color="green" on:click={(_) => { start() }}>启动</Button>
			{/if}
			{#if !running}
				<Button color="red" on:click={(_) => { delete_modal = true; }}>删除</Button>
			{/if}
		</div>
	</div>
	<div class="flex flex-row">
		<div class="flex flex-col">
			<div class="m-4">
				<div class="flex flex-row mb-1 align-middle items-center">
					<span class="text-1xl text-black-400 font-bold mx-2">
						状态:
					</span>
					<Button class="cursor-default" color={color_map(entry.state)}>{DeploymentState[entry.state]}</Button>
				</div>
				<Hr/>
				<div class="p-1 m-2">
					<span class="text-1xl text-black-400 font-bold mb-4">模型：</span>
					<div
						class="flex w-74 items-center px-5 mt-4 bg-white border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
					>
						<div class="w-20 max-w-20 min-w-[4rem]">
							<img src={`${$BACKEND}/openllm/avatar/${openllm_entry.model_id}`} alt="no img" />
						</div>
						<div class="flex flex-col justify-between p-4 leading-normal">
							<div class="flex flex-row justify-between">
								<h5
									class="mb-2 w-44 font-bold tracking-tight text-gray-900 dark:text-white"
								>
									{openllm_entry.model_name}
								</h5>
							</div>
							<p class="mb-3 font-normal text-gray-700 dark:text-gray-400">
								{openllm_entry.model_description}
							</p>
						</div>
					</div>
				</div>
			</div>
			{#if running}
				<Hr/>
			{/if}
			<div class="m-2">
				<span class={`text-1xl pt-1 text-black-400 font-bold ${running ? "" : "hidden"}`}>部署设备:</span>
				<div class={`m-1 ${running ? "": "hidden"}`}>
					{#each devices as device}
						{#if deployed_on == "auto" || deployed_on.includes(device.device_id)}
							<div class="inline-block border-gray-200 shadow p-2 m-2 w-40">
								<div class="m-2 text-md">CUDA:{device.device_id}</div>
								<hr class="m-1"/>
								<div class="m-2">
									GPU利用率：{device.gpu_utilization.toFixed(1)}%
									<Progressbar progress={device.gpu_utilization.toFixed(1)} />
								</div>
								<hr class="m-1"/>
								<div class="m-2">
									显存利用率：{device.memory_utilization.toFixed(1)}%
									<Progressbar progress={device.memory_utilization.toFixed(1)} />
								</div>
							</div>
						{/if}
					{/each}

				</div>
			</div>
			{#if running}
				<Hr />
				<div class="m-2">
					<span class="text-1xl pt-1 text-black-400 font-bold">Gradio API用例(Python):</span>
					<div class="flex flex-row gap-2 m-1">
						<Label class="mb-2">
							<div class="p-6 mt-4 bg-gray-100 rounded-md overflow-x-scroll w-[28rem]">
								<pre>
								<code>
{`from gradio_client import Client

client = Client("http://127.0.0.1:${entry.port}/")
result = client.predict(
	# str  in 'Message' Textbox component
	"Hello!!",	
	# float (numeric value between 0.1 and 3.0) in 'Temperature' Slider component
	0.1,
	# float (numeric value between 10 and 100) in 'Max Length' Slider component
	10,	
	api_name="/chat"
)
print(result)`}
								</code>
								</pre>
								</div>
						</Label>
					</div>
				</div>
				<div class="m-2">
					<span class="text-1xl pt-1 text-black-400 font-bold">Gradio API用例(Javascript):</span>
					<div class="flex flex-row gap-2 m-1">
						<Label class="mb-2">
							<div class="p-6 mt-4 bg-gray-100 rounded-md overflow-x-scroll w-[28rem]">
								<pre>
								<code>
{`import { client } from "@gradio/client";

const app = await client("http://127.0.0.1:${entry.port}/");
const result = await app.predict("/chat", [		
	// string  in 'Message' Textbox component
	"Hello!!", 		
	// number (numeric value between 0.1 and 3.0) in 'Temperature' Slider component
	0.1, 		
	// number (numeric value between 10 and 100) in 'Max Length' Slider component
	10, 
]);

console.log(result.data);`}
								</code>
								</pre>
								</div>
						</Label>
					</div>
				</div>
			{/if}
		</div>
		{#if running}
			<div class="flex w-2/3">
				<iframe 
					id="inlineFrameExample"
					title="Inline Frame Example"
					width=100%
					src={`http://127.0.0.1:${entry.port}`}>
				</iframe>
			</div>
		{/if}
		<div class="flex flex-col w-1/2">
			<div class="m-4">
				<span class="text-1xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;访问次数：</span>
				<Chart bind:options={access_chart} />
			</div>
		</div>
	</div>
</div>
{/if}
