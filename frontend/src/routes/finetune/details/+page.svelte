<script lang="ts">
	import {
		Button,
		Hr,
		Label,
		Tooltip,
		Toast,
		Accordion,
		AccordionItem,
		Modal,
		Checkbox,

		Toggle,

		Progressbar


	} from "flowbite-svelte";
	import { AngleLeftSolid, FireOutline, PapperPlaneOutline } from "flowbite-svelte-icons";
	import { page } from "$app/stores";
	import { onDestroy, onMount } from "svelte";
	import axios from "axios";
	import type LoggingRecord from "../../../class/LoggingRecord";
	import { BACKEND, LIST_SPLITTER, UPDATE_VIEW_INTERVAL } from "../../store";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	import type FinetuneEntry from "../../../class/FinetuneEntry";
	import {
		lora_specific_params,
		lora_quantization_params,
		lora_quantization_advanced,
		num_virt_tokens_param,
		training_params,
		training_advanced,
		type ParamEntry
	} from "../../components/params/Params"
	import FinetuneProgess from "../FinetuneProgess.svelte";
	import { goto } from "$app/navigation";
	import type EvalRecord from "../../../class/EvalRecord";
	import Charts from "./Charts.svelte";
	import type FinetuneEntryReduced from "../../../class/FinetuneEntryReduced";
	import { REALTIME_FINETUNE_DETAIL } from "../../store";
	import type CudaDeviceEntry from "../../../class/CudaDeviceEntry";
    import type DatasetEntry from "../../../class/DatasetEntry";
	let devices: Array<CudaDeviceEntry> = [];
	let devices_updater: number;
	onMount(async () => {
		async function update() {
			devices = (await axios.get(`${$BACKEND}/cuda/`)).data as Array<CudaDeviceEntry>;
		}
		devices = (await axios.get(`${$BACKEND}/cuda/`)).data as Array<CudaDeviceEntry>;
		devices_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(devices_updater);
	});

	let real_time_toggle = $REALTIME_FINETUNE_DETAIL;
	$: {
		$REALTIME_FINETUNE_DETAIL = real_time_toggle;
	}
	let real_time = false;
	REALTIME_FINETUNE_DETAIL.subscribe((v) => {
		real_time = v
	})
	const id = $page.url.searchParams.get("finetune_id");

	let finetune_entry: FinetuneEntry;
	let model_entry: OpenllmEntry;
	

	let finetune_entry_updater: number;
	let dataset_entry: DatasetEntry
	onMount(async () => {
		async function update() {
			if (finetune_entry.state == 0) {
				const reduced_entry = (await axios.get(`${$BACKEND}/finetune_entry/reduced/${id}`)).data as FinetuneEntryReduced;
				if(reduced_entry.state == 1) {
					setTimeout(() => {
						finetune_entry.state = reduced_entry.state
					}, UPDATE_VIEW_INTERVAL * 2)
				}
				else{
					finetune_entry.state = reduced_entry.state
				}
			}
		}
		finetune_entry = (await axios.get(`${$BACKEND}/finetune_entry/${id}`)).data;
		model_entry = (await axios.get(`${$BACKEND}/openllm/${finetune_entry.model_id}`)).data;
		dataset_entry = (await axios.get(`${$BACKEND}/dataset_entry/${finetune_entry.dataset_id}`)).data;
		finetune_entry_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
	});
	onDestroy(() => {
		clearInterval(finetune_entry_updater);
	});


	interface ParamGroup {
		title: string;
		advanced: boolean;
		params: Array<{
			name: string;
			value: string;
		}>;
	}

	let groups: Array<ParamGroup> = [];
	let adapter_name: string = "";

	function parse_into_param_groups(entry: FinetuneEntry) {
		return {
			lora_specific_params: {
				title: "lora参数",
				advanced: false,
				params: lora_specific_params.map((entry) => {
					return {
						name: entry.var_name,
						value: finetune_entry[entry.var_name]
					};
				})
			},
			lora_quantization_params: {
				title: "qlora量化参数",
				advanced: false,
				params: [
					{
						name: lora_quantization_params[0].var_name,
						value: finetune_entry.load_4bit ? "4" : "8"
					}
				]
			},
			lora_quantization_advanced: {
				title: "qlora量化参数（高级）",
				advanced: true,
				params: lora_quantization_advanced.map((entry) => {
					return {
						name: entry.var_name,
						value: finetune_entry[entry.var_name]
					};
				})
			},
			num_virt_tokens_param: {
				title: "虚拟token参数",
				advanced: false,
				params: num_virt_tokens_param.map((entry) => {
					return {
						name: entry.var_name,
						value: finetune_entry[entry.var_name]
					};
				})
			},
			train_params: {
				title: "训练参数",
				advanced: false,
				params: training_params.map((entry) => {
					return {
						name: entry.var_name,
						value: finetune_entry[entry.var_name]
					};
				})
			},
			training_advanced: {
				title: "训练参数（高级）",
				advanced: true,
				params: training_advanced.map((entry) => {
					return {
						name: entry.var_name,
						value: finetune_entry[entry.var_name]
					};
				})
			}
		};
	}

	$: {
		if(finetune_entry != undefined) {
			const g = parse_into_param_groups(finetune_entry);
			if (finetune_entry.adapter_name == "lora" && !finetune_entry.bits_and_bytes) {
				groups = [g.lora_specific_params, g.train_params, g.training_advanced];
				adapter_name = "lora";
			} else if (finetune_entry.adapter_name == "lora" && finetune_entry.bits_and_bytes) {
				groups = [
					g.lora_specific_params,
					g.lora_quantization_params,
					g.train_params,
					g.lora_quantization_advanced,
					g.training_advanced
				];
				adapter_name = "qlora";
			} else {
				adapter_name = finetune_entry.adapter_name;
				groups =
					finetune_entry.adapter_name.toLowerCase() == "IA3" ? [] : [g.num_virt_tokens_param];
				groups = groups.concat([g.train_params, g.training_advanced]);
			}
		}
	}

	let delete_modal = false;
	let double_check = false;

	async function delete_entry_handle() {
		await axios.delete(`${$BACKEND}/finetune_entry/${id}`);
		goto("/finetune");
	}

	let stop_modal = false

	async function stop_handle() {
		axios.put(`${$BACKEND}/finetune/stop/${id}`)
	}
</script>


<Modal title="确认打断" bind:open={stop_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要打断训练吗？</p>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">程序不会立即停止训练，而是将在输入打断信号后的第一个训练step后结束训练。</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		训练的进度和结果将<span class="font-bold">不会</span>被保存。
	</p>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				color="red"
				on:click={() => {
					stop_handle();
				}}>是的</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

<Modal title="确认删除" bind:open={delete_modal} autoclose>
	<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">确认要删除吗？</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		删除后，该任务的所有相关信息将<span class="font-semibold">无法</span>恢复。
	</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		如果希望保存模型，请使用页面上的保存功能。
	</p>
	<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
		如果该任务的输出文件夹中包含其它文件，它们会被<span class="font-semibold">一并</span>删除。
	</p>
	<div class="flex flex-row justify-end p-2 m-2 align-middle items-center">
		我确认要<span class="font-semibold text-red-600">删除</span>该任务记录及其相关文件
		<Checkbox class="mx-2" bind:checked={double_check} />
	</div>
	<svelte:fragment slot="footer">
		<div class="w-full flex justify-end gap-2">
			<Button
				disabled={!double_check}
				color="red"
				on:click={() => {
					delete_entry_handle();
				}}>删除</Button
			>
			<Button color="alternative">不</Button>
		</div>
	</svelte:fragment>
</Modal>

{#if finetune_entry == undefined || dataset_entry == undefined || model_entry == undefined}
loading
{:else}

<div>
	<div class="flex flex-row justify-between">
		<div class="flex">
			<div class="">
				<Button href="/finetune">
					<AngleLeftSolid size="sm" />返回
				</Button>
			</div>
			<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;详细信息</span>
			<div class="flex flex-row mx-2 p-2">
				<span class="mx-2">实时数据</span>
				<Toggle bind:checked={real_time_toggle}/>
			</div>
		</div>
		<div class="flex gap-2">
			<Button color="red" class={`${finetune_entry.state == 0 ? "": "hidden"}`} on:click={(_) => {stop_modal = true}}>打断</Button>
			<Button href="/deployment/tasks" class={`${finetune_entry.state == 1 ? "" : "hidden"}`} color="blue">部署</Button>
			<Button
				on:click={(_) => {
					delete_modal = true;
				}}
				class={`${finetune_entry.state != 0 ? "" : "hidden"}`}
				color="red"
			>
				删除
			</Button>
		</div>
	</div>
	<div class="flex flex-row">
		<div class="flex flex-col w-1/3">
			<div class="m-4">
				<div class="flex flex-row mb-1 items-center w-full">
					<span class="text-1xl pt-1 text-black-400 font-bold">模型：</span>
					<div class="pl-2 w-[80%]">
						{#if finetune_entry.state == 0}
							<div class="flex flex-row w-full">
								<Button class="cursor-default" color="blue">训练中</Button>
								<div class="m-2 p-2 w-[50%]">
									<FinetuneProgess {id} />
								</div>
							</div>
						{:else if finetune_entry.state == 1}
							<Button class="cursor-default" color="green">训练完成</Button>
						{:else if finetune_entry.state == -1}
							<Button class="cursor-default" color="red">训练出错</Button>
						{:else}
							无效状态码
						{/if}
					</div>
				</div>
				<div class="p-1">
					{#if model_entry === undefined}
						<div
							class="flex w-74 items-center px-5 bg-white border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
						>
							loading...
						</div>
					{:else}
						<div
							class="p-4 flex w-74 items-center px-5 bg-white border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
						>
							<div class="w-20 max-w-20 min-w-[4rem]">
								<img src={`${$BACKEND}/openllm/avatar/${model_entry.model_id}`} alt="no img" />
							</div>
							<div
								class="w-full flex flex-col justify-between p-4 leading-normal items-center"
							>
								<h5
									class="mb-2 font-bold tracking-tight text-gray-900 dark:text-white"
								>
									{model_entry.model_name}
								</h5>
							</div>
						</div>
					{/if}
				</div>
			</div>
			<Hr/>
			<div class="grid gap-2 m-4 grid-cols-1 lg:grid-cols-2">
				<div>
					<Label for="first_name" class="mb-2">
						训练方法: {adapter_name}
					</Label>
				</div>
			</div>
			{#each groups.filter((g) => {
				return !g.advanced;
			}) as group}
				<Hr />
				<div class="m-1">
					<span class="text-1xl pt-1 text-black-400 font-bold">{group.title}</span>
					<div class="grid gap-2 m-2 grid-cols-1 lg:grid-cols-2">
						{#each group.params as param}
							<div>
								<Label for="first_name" class="mb-2">
									{param.name}: {param.value}
								</Label>
							</div>
						{/each}
					</div>
				</div>
			{/each}
			<Hr />
			<div class="m-1">
				<span class="text-1xl pt-1 text-black-400 font-bold">训练设备当前状态:</span>
				<div class="gap-2 m-1 grid grid-cols-1 lg:grid-cols-2">
					{#each finetune_entry.devices == "auto" ? devices.map((each) => {return each.device_id}) : finetune_entry.devices.split(LIST_SPLITTER) as device}
						<div class="inline-block border-gray-200 shadow p-2 m-2 w-40">
							<div class="m-2 text-md">CUDA:{devices[device].device_id}</div>
							<hr class="m-1"/>
							<div class="m-1">
								GPU利用率：{devices[device].gpu_utilization.toFixed(1)}%
								<Progressbar progress={devices[device].gpu_utilization.toFixed(1)} />
							</div>
							<hr class="m-1"/>
							<div class="m-1">
								显存利用率：{devices[device].memory_utilization.toFixed(1)}%
								<Progressbar progress={devices[device].memory_utilization.toFixed(1)} />
							</div>
						</div>
					{/each}
				</div>
			</div>
			<Hr />
			<div class="m-1">
				<span class="text-1xl pt-1 text-black-400 font-bold">数据集</span>
				<div class="m-1">
					<div>{dataset_entry.name}</div>
					<div class="mt-1 p-2 text-sm text-gray-800">{dataset_entry.description}</div>
				</div>
			</div>
			<Hr />
			<div class="m-1">
				<span class="text-1xl pt-1 text-black-400 font-bold">保存路径:</span>
				<div class="flex flex-row gap-2 m-1">
					<Label class="mb-2">
						{finetune_entry.output_dir}
					</Label>
				</div>
			</div>
			<Accordion>
				<AccordionItem>
					<span slot="header">高级</span>
					{#each groups.filter((g) => {
						return g.advanced;
					}) as group, index}
						<div class="m-1">
							<span class="text-1xl pt-1 text-black-400 font-bold">{group.title}</span
							>
							<div class="grid grid-cols-1 gap-2 m-2">
								{#each group.params as param}
									<div>
										<Label for="first_name" class="mb-2">
											{param.name}: {param.value}
										</Label>
									</div>
								{/each}
							</div>
						</div>
						{#if index != groups.reduce((acc, g) => {
								return acc + (g.advanced ? 1 : 0);
							}, 0) - 1}
							<Hr />
						{/if}
					{/each}
				</AccordionItem>
			</Accordion>
		</div>
		<div class="w-2/3 grid grid-cols-1 lg:grid-cols-2 p-4">
			<Charts finetuneEntry={finetune_entry} id={id} realTime={real_time}/>
		</div>
	</div>
</div>

{/if}