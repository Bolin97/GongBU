<script lang="ts">
	import axios from "axios";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	import { onMount } from "svelte";
	let models = [] as Array<OpenllmEntry>;
	onMount(async () => {
		models = (await axios.get(`/api/openllm`)).data;
	});

	export let selectedId = "";
</script>

<!-- <div class="grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 p-2"> -->
{#each models as model, index}
	<button
		on:click={(_) => (selectedId = model.model_id)}
		class="m-1 w-[40rem] p-1 rounded inline-grid"
	>
		<div class="p-1">
			<div
				class="flex w-74 items-center text-left px-5 bg-white border {selectedId ==
				model.model_id
					? 'border-blue-600'
					: 'border-gray-200'} rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
			>
				<div class="w-20 max-w-20 min-w-[4rem]">
					<img src={`/api/openllm/avatar/${model.model_id}`} alt="no img" />
				</div>
				<div class="flex flex-col justify-between p-4 leading-normal">
					<div class="flex flex-row justify-between">
						<h5
							class="mb-2 w-44 font-bold tracking-tight text-gray-900 dark:text-white"
						>
							{model.model_name}
						</h5>
					</div>
					<p class="mb-3 font-normal text-gray-700 dark:text-gray-400">
						{model.model_description}
					</p>
				</div>
			</div>
		</div>
	</button>
{/each}
<!-- </div> -->
