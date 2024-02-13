<script lang="ts">
	import { StepIndicator, Button } from "flowbite-svelte";
	import { Input, Timeline, TimelineItem } from "flowbite-svelte";
	import {
		CalendarWeekSolid,
		CheckCircleOutline,
		AdjustmentsHorizontalSolid
	} from "flowbite-svelte-icons";
	import axios from "axios";
	import Device from "./Device.svelte";
	import { BACKEND } from "../../store";
	import Model from "./Model.svelte";
	import Time from "./Time.svelte";
	import Params from "./Params.svelte";
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	let currentStep = 1;
	function toLocalISOString(date: any) {
		const tzoffset = date.getTimezoneOffset() * 60000; // offset in milliseconds
		const localISOTime = (new Date(date - tzoffset)).toISOString().slice(0, 16);
		return localISOTime;
	}
	let selected_model: string = "";
	let deploy_finetuned: boolean = false;
	let startdate: string = toLocalISOString(new Date());
	let enddate: string = toLocalISOString(new Date());
	let name = "";
	let description = "";
	let port: number = 7860;
	let devices: Array<number> | "auto" = [];
	const steps = ["模型选择", "参数设置", "设备选择", "部署时间", "项目名称"];

	const stepsDescription = [
		"选择合适的开源或已微调大模型",
		"选择应用的启动参数",
		"选择设备",
		"确定微调输出路径",
		"输入项目名称与描述"
	];

	const url_params = $page.url.searchParams;
	if(url_params.has("model_id")) {
		selected_model = url_params.get("model_id") as string;
		deploy_finetuned = false;
		currentStep = 2;
	}

	let params: any = {
		"bits_and_bytes": false,
		"load_xbit": 8,
	};
	$: deploy_params = {
		"model_or_finetune_id": selected_model,
		"deploy_finetuned": deploy_finetuned,
		"start_time":new Date(startdate).toISOString().slice(0, 16),
		"end_time": new Date(enddate).toISOString().slice(0, 16),
		"params": params,
		"devices": devices,
	}

	async function submit_handle() {
		await axios.post(`${$BACKEND}/deploy/`, deploy_params, {
			params: {
				name: name,
				description: description,
				port: port
			}
		});
		goto("/deployment");
	}
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;创建部署任务</span>
	<span class="text-1xl pt-2 text-black-400 text-center"
		>&nbsp;&nbsp;按照提示步骤创建部署任务</span
	>
</div>
<hr class="pt-1" />
<div class="w-full flex flex-row p-1 m-2 mt-4">
	<div>
		<Timeline order="vertical">
			{#each steps as step, i}
				<TimelineItem title={step} date="">
					<svelte:fragment slot="icon">
						<span
							class="flex absolute -left-3 justify-center items-center w-6 h-6 bg-primary-200 rounded-full ring-8 ring-white dark:ring-gray-900 dark:bg-primary-900"
						>
							{#if i + 1 === currentStep}
								<AdjustmentsHorizontalSolid
									size="sm"
									class="text-primary-500 dark:text-primary-400"
								/>
							{:else if i + 1 < currentStep}
								<CheckCircleOutline
									size="sm"
									class="text-primary-500 dark:text-primary-400"
								/>
							{:else}
								<CalendarWeekSolid
									size="sm"
									class="text-primary-500 dark:text-primary-400"
								/>
							{/if}
						</span>
					</svelte:fragment>
					<p class="mb-4 text-base font-normal text-gray-500 dark:text-gray-400">
						{stepsDescription[i]}
					</p>
				</TimelineItem>
			{/each}
		</Timeline>
	</div>
	<div class="w-full m-2">
		<StepIndicator {currentStep} {steps} color="blue" />
		<div>
			<div class={`${currentStep == 1 ? "" : "hidden"}`}>
				<Model bind:selectedId={selected_model} bind:deployFinetuned={deploy_finetuned}/>
			</div>
			<div class={`${currentStep == 2 ? "" : "hidden"}`}>
				<Params bind:params={params}/>
			</div>
			<div class={`${currentStep == 3 ? "" : "hidden"}`}>
				<Device bind:useDevices={devices} updaterOn={currentStep == 3}/>
			</div>
			<div class={`${currentStep == 4 ? "" : "hidden"}`}>
				<Time bind:start={startdate} bind:end={enddate} />
			</div>
			<div class={`${currentStep == 5 ? "" : "hidden"}`}>
				<div class="m-2 p-2">
					<div class="my-4">
						<span class="font-semibold text-lg m-2">任务名称：</span>
						<Input class="my-2" bind:value={name} placeholder="在此输入任务名称" />
					</div>
					<div class="my-4">
						<span class="font-semibold text-lg m-2">任务描述：</span>
						<Input
							class="my-2"
							bind:value={description}
							placeholder="在此输入任务描述"
						/>
					</div>
					<div class="my-4">
						<span class="font-semibold text-lg m-2">部署端口号：</span>
						<Input
							class="my-2"
							bind:value={port}
							type="number"
							placeholder="在此输入部署的端口号"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="flex flex-row-reverse gap-5 m-2">
			{#if currentStep === 5}
				<Button on:click={(_) => {
					submit_handle();
				}}>完成</Button>
			{:else if currentStep === 4}
				<Button disabled={enddate <= startdate} on:click={(_) => ++currentStep}>下一步</Button>
			{:else if currentStep === 3}
				<Button on:click={(_) => ++currentStep}>下一步</Button>
			{:else if currentStep === 2}
				<Button on:click={(_) => ++currentStep}
				>下一步</Button>
			{:else if currentStep === 1}
				<Button disabled={selected_model.length === 0} on:click={(_) => ++currentStep}
				>下一步</Button>
			{/if}
			<Button class={currentStep === 1 ? "hidden" : ""} on:click={(_) => --currentStep}
				>上一步</Button>
		</div>
	</div>
</div>
