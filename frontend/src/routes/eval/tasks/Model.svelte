<script lang="ts">
	import axios from "axios";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	import type FinetuneEntry from "../../../class/FinetuneEntry";
	import { Kbd } from "flowbite-svelte";
	import { onMount } from "svelte";
	
	let entries = [] as Array<FinetuneEntry>;
	let models = [] as Array<OpenllmEntry>;
	onMount(async () => {
		entries = (await axios.get(`api/finetune_entry`)).data as Array<FinetuneEntry>;
		models = (await axios.get(`api/openllm/`)).data;
	});
	$:model_id_to_view_pic = models.reduce((acc, cur) => {
  		acc[cur.model_id] = cur.view_pic;
  		return acc;
	}, {});
	export let selectedId = "";
	export let evalFinetuned: boolean | null = null;
    
</script>

{#each models as model, index}
		<button on:click={(_) => {
			selectedId = model.model_id;
			evalFinetuned = false;
		}}
			class="m-1 w-[36rem] p-1 rounded inline-grid">
			<div class="p-1">
				<div
					class="flex w-74 items-center text-left px-5 bg-white border {selectedId ==
					model.model_id && !evalFinetuned
						? 'border-blue-600'
						: 'border-gray-200'} rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
				>
					<div class="w-20 max-w-20 min-w-[4rem]">
						<img src={`api/openllm/avatar/${model.model_id}`} alt="no img" />
					</div>
					<div class="flex flex-col justify-between p-4 leading-normal">
						<div class="flex flex-row justify-between">
							<h5
								class="mb-2 w-44 font-bold tracking-tight text-gray-900 dark:text-white"
							>
								{model.model_name}
							</h5>
							<Kbd class="px-2 py-1.5 min-w-[3rem]">base</Kbd>
						</div>
						<p class="mb-3 font-normal text-gray-700 dark:text-gray-400">
							{model.model_description}
						</p>
					</div>
				</div>
			</div>
		</button>
{/each}
{#each entries as entry, index}
	{#if entry.state == 1}
		<button on:click={(_) => {
			selectedId = entry.id.toString();
			evalFinetuned = true;
			}}
			class="m-1 w-[36rem] p-1 rounded inline-grid">
			<div class="p-1">
				<div
					class="flex w-74 items-center text-left px-5 bg-white border {selectedId ==
					entry.id.toString() && evalFinetuned
						? 'border-blue-600'
						: 'border-gray-200'} rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
				>
					<div class="w-20 max-w-20 min-w-[4rem]">
						<img src={`api/openllm/avatar/${entry.model_id}`} alt="no img" />
					</div>
					<div class="flex flex-col justify-between p-4 leading-normal">
						<div class="flex flex-row justify-between">
							<h5
								class="mb-2 w-44 font-bold tracking-tight text-gray-900 dark:text-white"
							>
								{entry.name}
							</h5>
							<Kbd class="px-2 py-1.5 min-w-[3rem]">finetune</Kbd>
						</div>
						<p class="mb-3 font-normal text-gray-700 dark:text-gray-400">
							{entry.description}
						</p>
					</div>
				</div>
			</div>
		</button>
	{/if}
{/each}
