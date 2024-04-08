<script lang="ts">
	import { Checkbox, Label, Progressbar, Radio, Toggle } from "flowbite-svelte";
	import type CudaDeviceEntry from "../../../class/CudaDeviceEntry";
	import { onDestroy, onMount } from "svelte";
	import axios from "axios";
	import { UPDATE_VIEW_INTERVAL } from "../../store";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	import { PlusSolid, CheckCircleOutline } from "flowbite-svelte-icons";
	let devices: Array<CudaDeviceEntry> = [];
	export let updaterOn = true;
	
	let devices_updater: number;
	onMount(async () => {
		async function update() {
			if (updaterOn) {
				devices = (await axios.get(`/api/cuda/`)).data as Array<CudaDeviceEntry>;
			}
		}
		devices = (await axios.get(`/api/cuda/`)).data as Array<CudaDeviceEntry>;
		devices_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(devices_updater);
	});

	function clickHandle(id: number) {
		if(!auto_dist && useDevices != "auto") {
			if (useDevices.includes(id)) {
				useDevices = useDevices.filter((value) => value != id);
			} else {
				useDevices = [...useDevices, id];
			}
		}
	}
	let auto_dist = false;
	function toggle_auto() {
		if(useDevices == "auto") {
			useDevices = []
		}
		else {
			useDevices = "auto"
		}
		auto_dist = !auto_dist;
	}
	export let useDevices: number[] | "auto" = [] as number[];
</script>

<div class="flex flex-col">
	<!-- <span class="text-1xl m-2 mt-4">已选择的模型与微调方法<span class="mx-1 px-1"><span class="font-bold">{allow_multi ? "": "不"}</span>支持</span>多卡微调</span> -->
	<div class="flex flex-row justify-between">
		<span class="text-1xl m-2 mt-4">自动分配</span>
		<Toggle on:change={(_) => { toggle_auto() }}/>
	</div>
	<div class="text-1xl m-2 my-4 mt-2">本地设备：</div>
	<div class={`flex flex-col ${auto_dist ? "opacity-50" : ""}`}>
		<div class="m-2 flow-root">
			{#each devices as device}
				<button
					class={`m-2 p-2 inline-grid w-60 border ${
						!(useDevices == "auto" || useDevices.includes(device.device_id))
							? "border-gray-200"
							: "border-blue-600"
					} rounded shadow-sm text-left gap-2`}
					on:click={(_) => clickHandle(device.device_id)}
				>
					<div class="m-2">
						{#if useDevices == "auto" || useDevices.includes(device.device_id)}
							<CheckCircleOutline size="sm" class="text-blue-600"/>
						{:else}
							<PlusSolid size="sm" class="text-gray-400"/>
						{/if}
					
						<div class="m-2 text-lg">CUDA:{device.device_id}</div>
						<div class="m-2">
							GPU利用率：{device.gpu_utilization.toFixed(1)}%
							<Progressbar progress={device.gpu_utilization.toFixed(1)} />
						</div>
						<div class="m-2">
							显存利用率：{device.memory_utilization.toFixed(1)}%
							<Progressbar progress={device.memory_utilization.toFixed(1)} />
						</div>
					</div>
				</button>
			{/each}
		</div>
	</div>
</div>
