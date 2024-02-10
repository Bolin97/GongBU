<script lang="ts">
	import { StepIndicator, Button, Label, Input, Tooltip } from "flowbite-svelte";
	import { Timeline, TimelineItem } from "flowbite-svelte";
	import {
		CalendarWeekSolid,
		CheckCircleSolid,
		AdjustmentsHorizontalSolid
	} from "flowbite-svelte-icons";
	import Model from "./Model.svelte";
	import Finetuning from "./Finetuning.svelte";
	import Data from "./Data.svelte";
	import Device from "./Device.svelte";
	import Output from "./Output.svelte";
	import { fade } from "svelte/transition";
	import { page } from "$app/stores";
	import { default_finetune_params } from "../../../class/FinetuneParams";
	import Eval from "./Eval.svelte";
	import axios from "axios";
	import { BACKEND, DEFAULT_MODEL_OUTPUT } from "../../store";
	import { goto } from "$app/navigation";
	import type OpenllmEntry from "../../../class/OpenllmEntry";

	let current_step = 1;
	let selected_model_id: string = "";
	let selected_dataset_id: string = "";
	let use_devices: Array<number> | "auto" = [];
	let dir_arr = $DEFAULT_MODEL_OUTPUT.split("/").filter((x) => x != "");
	let evals = [];
	let name = "";
	let description = "";
	$: output_dir = "/".concat(dir_arr.join("/"));

	let finetune_params = default_finetune_params();

	let model_entry: OpenllmEntry = {
		model_id: "",
		model_name: "",
		model_description: "",
		view_pic: "",
		remote_path: "",
		local_path: "",
		local_store: 0,
		lora_support: 0,
		lora_multi_device: 0,
		prefix_tuning_support: 0,
		prefix_tuning_multi_device: 0,
		ptuning_support: 0,
		ptuning_multi_device: 0,
		prompt_tuning_support: 0,
		prompt_tuning_multi_device: 0,
		IA3_support: 0,
		IA3_multi_device: 0,
		storage_state: "",
		storage_date: "",
		finetune: 0,
		deployment: 0
	}
	$: {
		if(current_step == 2) {
			axios.get(`${$BACKEND}/openllm/${selected_model_id}`).then((res) => {
				model_entry = res.data
			})
		}
	}

	$: {
		finetune_params.devices = use_devices;
		finetune_params.dataset_id = selected_dataset_id.toString();
		finetune_params.model_id = selected_model_id.toString();
		finetune_params.output_dir = output_dir;
		finetune_params.eval_indexes = evals;
	}

	const params = $page.url.searchParams;
	if (params.has("model_id")) {
		selected_model_id = params.get("model_id");
		current_step = 2;
	}

	const steps = [
		"模型选择",
		"数据选择",
		"评估指标",
		"微调方法",
		"设备选择",
		"输出选择",
		"项目名称"
	];

	const steps_description = [
		"选择合适的开源大模型",
		"选择已上传到数据池的数据",
		"选择评估指标",
		"选择平台支持的微调方法并配置参数",
		"选择可支持微调的本地设备",
		"确定微调输出路径",
		"输入项目名称与描述"
	];

	async function submit_handle() {
		await axios.post(`${$BACKEND}/finetune/`, finetune_params, {
			params: {
				name: name,
				description: description
			}
		});
		goto("/finetune");
	}

	$: device_updater_on = current_step == 5;
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;创建微调任务</span>
	<span class="text-1xl pt-2 text-black-400 text-center"
		>&nbsp;&nbsp;按照提示步骤创建微调任务</span
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
							{#if i + 1 === current_step}
								<AdjustmentsHorizontalSolid
									size="sm"
									class="text-primary-500 dark:text-primary-400"
								/>
							{:else if i + 1 < current_step}
								<CheckCircleSolid
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
						{steps_description[i]}
					</p>
				</TimelineItem>
			{/each}
		</Timeline>
	</div>
	<div class="w-full m-2">
		<StepIndicator currentStep={current_step} {steps} color="blue" />
		<div>
			<div class={`${current_step == 1 ? "" : "hidden"}`}>
				<Model bind:selectedId={selected_model_id} />
			</div>
			<div class={`${current_step == 2 ? "" : "hidden"}`}>
				<Data bind:selectedSet={selected_dataset_id} />
			</div>
			<div class={`${current_step == 3 ? "" : "hidden"}`}>
				<Eval bind:indexes={evals} />
			</div>
			<div class={`${current_step == 4 ? "" : "hidden"}`}>
				<Finetuning modelEntry={model_entry} bind:finetuneParam={finetune_params} />
			</div>
			<div class={`${current_step == 5 ? "" : "hidden"}`}>
				<Device bind:useDevices={use_devices} bind:updaterOn={device_updater_on} adapter={finetune_params.adapter_name} modelEntry={model_entry}/>
			</div>
			<div class={`${current_step == 6 ? "" : "hidden"}`}>
				<Output bind:dirArr={dir_arr} />
			</div>
			<div class={`${current_step == 7 ? "" : "hidden"}`}>
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
				</div>
			</div>
		</div>
		<div class="flex flex-row-reverse gap-5 m-2">
			{#if current_step === 7}
				<Button
					on:click={(_) => {
						submit_handle();
					}}>完成</Button
				>
			{:else if current_step === 6}
				<Button on:click={(_) => ++current_step}>保存模型到当前位置</Button>
			{:else if current_step === 5}
				<Button disabled={use_devices.length === 0} on:click={(_) => ++current_step}
					>下一步</Button
				>
				{#if use_devices.length === 0}
				<Tooltip>至少选择一个设备</Tooltip>
				{/if}
			{:else if current_step == 2}
				<Button disabled={selected_dataset_id.length === 0} on:click={(_) => ++current_step}
					>下一步</Button
				>
			{:else if current_step === 1}
				<Button disabled={selected_model_id.length === 0} on:click={(_) => ++current_step}
					>下一步</Button
				>
			{:else}
				<Button on:click={(_) => ++current_step}>下一步</Button>
			{/if}
			<Button class={current_step === 1 ? "hidden" : ""} on:click={(_) => --current_step}
				>{"上一步"}</Button
			>
		</div>
	</div>
</div>
