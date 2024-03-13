<script lang="ts">
	import { StepIndicator, Button, Modal, Hr } from "flowbite-svelte";
	import { Timeline, TimelineItem } from "flowbite-svelte";
	import Information from "./Information.svelte";
	import Dataset from "../DatasetTable.svelte";
	import {
		CalendarWeekSolid,
		CheckCircleOutline,
		AdjustmentsHorizontalSolid,
		AngleLeftSolid
	} from "flowbite-svelte-icons";
	import { goto } from "$app/navigation";
	import axios from "axios";
	import { BACKEND } from "../../store";
	import type FinetuneDatasetEntry from "../../../class/DatasetEntry";
	import type DatasetEntry from "../../../class/DatasetEntry";
	import Uploader from "../Uploader.svelte";
	import { onMount } from "svelte";
	let current_step = 1;
	let name = "";
	let description = "";

	let loading = false;
	let pool_id: number = -1;
	if (pool_id == null) {
		loading = true;
	}

	async function create_pool_handle() {
		loading = true;
		const form = new FormData();
		form.append("name", name);
		form.append("description", description);
		pool_id = (
			await axios.post(
				`${$BACKEND}/pool`,
				{},
				{
					params: {
						name: name,
						description: description
					}
				}
			)
		).data as number;
		loading = false;
	}

	let stage_empty: boolean;

	const steps = ["基本信息", "上传数据"];

	const steps_description = ["填写所创建数据池的基本信息", "选择需要上传的数据"];

	let next_modal = false;

	function next_handle() {
		if (stage_empty) {
			goto(`/data`);
		} else {
			next_modal = true;
		}
	}

	function return_handle() {
		if(current_step == 1) {
			goto(`/data`);
		}
		else if (stage_empty) {
			goto(`/data`);
		} else {
			next_modal = true;
		}
	}
</script>

{#if !loading}
	<Modal title="暂存区中仍有未提交的数据" bind:open={next_modal} autoclose>
		<p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
			确认已创建完成吗？暂存区中仍有未提交的数据。
		</p>
		<p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
			暂存区的数据将<span class="font-semibold">不会</span>被保存。
		</p>
		<svelte:fragment slot="footer">
			<div class="w-full flex justify-end gap-2">
				<Button
					color="red"
					on:click={() => {
						goto(`/data`);
					}}>是的</Button
				>
				<Button color="alternative">不</Button>
			</div>
		</svelte:fragment>
	</Modal>

	<div class="pt-2 w-full flex flex-row">
		<div class="flex flex-row">
			<Button
				on:click={(_) => {
					return_handle();
				}}
			>
				<AngleLeftSolid size="sm" />返回
			</Button>
		</div>
		<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;创建数据池</span>
		<span class="text-1xl pt-2 text-black-400 text-center"
			>&nbsp;&nbsp;按照提示步骤创建数据池</span
		>
	</div>
	<Hr/>
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
							{steps_description[i]}
						</p>
					</TimelineItem>
				{/each}
			</Timeline>
		</div>
		<div class="w-full m-2">
			<StepIndicator currentStep={current_step} {steps} color="blue" />
			<div>
				{#if current_step == 1}
					<Information bind:name bind:description />
				{:else}
					<Uploader bind:stageEmpty={stage_empty} poolId={pool_id} />
				{/if}
			</div>
			<div class="flex gap-5 m-2 justify-end">
				<div>
					{#if current_step === 2}
						<Button
							on:click={(_) => {
								next_handle();
							}}>完成</Button
						>
					{:else}
						<Button
							disabled={name.length == 0 || description.length == 0}
							on:click={async (_) => {
								await create_pool_handle();
								++current_step;
							}}>创建数据池</Button
						>
					{/if}
				</div>
			</div>
		</div>
	</div>
{:else}
	<div>loading</div>
{/if}
