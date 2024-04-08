<script lang="ts">
	import type OpenllmEntry from "../../class/OpenllmEntry";
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import axios from "axios";
	let models = [] as Array<OpenllmEntry>;
	onMount(async () => {
		models = (await axios.get(`/api/openllm`)).data;
	});
</script>

<div class="pt-2 w-full">
	<span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;模型广场</span>
	<span class="text-1xl pt-2 text-black-400 text-center"
		>&nbsp;&nbsp;集中展示与管理预置开源大模型，支持对模型进行微调与部署</span
	>
</div>
<hr class="pt-1" />

{#if models.length != 0}
	{#each models as model}
		<div class="p-1 w-[40rem] inline-grid">
			<div
				class="flex items-center px-5 bg-white border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
			>
				<div class="w-20 h-20 max-w-20 min-w-[4rem]">
					<img src={`/api/openllm/avatar/${model.model_id}`} alt="no img" />
				</div>
				<div class="flex flex-col justify-between p-4 leading-normal">
					<div class="flex flex-row justify-between">
						<h5
							class="mb-2 text-2xl w-60 font-bold tracking-tight text-gray-900 dark:text-white"
						>
							{model.model_name}
						</h5>
						<div class="flex flex-row justify-between">
							<button
								on:click={(_) => goto(`/finetune/tasks?model_id=${model.model_id}`)}
								type="button"
								class="text-white bg-[#1da1f2] hover:bg-[#1da1f2]/90 focus:ring-4 focus:outline-none focus:ring-[#1da1f2]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#1da1f2]/55 me-2 mb-2"
							>
								微调
							</button>
							<button
								on:click={(_) => goto(`/deployment/tasks?model_id=${model.model_id}`)}
								type="button"
								class="text-white bg-[#4285F4] hover:bg-[#4285F4]/90 focus:ring-4 focus:outline-none focus:ring-[#4285F4]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#4285F4]/55 me-2 mb-2"
							>
								部署
							</button>
						</div>
					</div>
					<p class="mb-3 font-normal text-gray-700 dark:text-gray-400">
						{model.model_description}
					</p>
				</div>
			</div>
		</div>
	{/each}
{/if}
