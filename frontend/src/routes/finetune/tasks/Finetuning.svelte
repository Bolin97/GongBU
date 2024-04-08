<script lang="ts">
	import { Radio, Label, Input, Hr, Accordion, AccordionItem, Button } from "flowbite-svelte";
	import ParamGroup from "../../components/params/ParamGroup.svelte";
	import {
		type ParamEntry,
		ParamType,
		param_component_mapper,
		default_finetune_params,
		num_virt_tokens_param,
		lora_quantization_params,
		lora_quantization_advanced,
		training_params,
		training_advanced
	} from "../../components/params/Params";
	import type { FinetuneParams } from "../../../class/FinetuneParams";
	const adapters: Array<"lora" | "qlora" | "p-tuning" | "prefix-tuning" | "prompt-tuning" | "IA3" | "lokr" | "loha"> = ["lora", "qlora", "p-tuning", "prefix-tuning", "prompt-tuning", "IA3", "lokr", "loha"];
	import { lora_specific_params } from "../../components/params/Params";
	import type OpenllmEntry from "../../../class/OpenllmEntry";
	let adapter = "lora";
	let params = default_finetune_params();
	export let finetuneParam: FinetuneParams;
	$: {
		Object.keys(params).forEach((k) => {
			if (k in finetuneParam) {
				finetuneParam[k] = params[k];
			}
		});
		finetuneParam.adapter_name = adapter == "qlora" ? "lora" : adapter;
		finetuneParam.bits_and_bytes = adapter == "qlora";
		finetuneParam.load_4bit = params.load_xbit == 4;
		finetuneParam.load_8bit = params.load_xbit == 8;
		// finetuneParam.save_step = params.eval_step;
	}

</script>

<div>
	<div class="flex flex-row gap-2 m-2 my-10">
		<span>微调方法选择：</span>
		{#each adapters as adapter_name}
			<Radio bind:group={adapter} name="method" value={adapter_name}
				><p class="text-lg">{adapter_name}</p></Radio
			>
		{/each}
	</div>
	{#if adapter == "lora" || adapter == "qlora" || adapter == "lokr" || adapter == "loha"}
		<ParamGroup title="lora参数" entries={lora_specific_params} bind:params />
			{#if adapter == "qlora"}
				<ParamGroup title="lora量化参数" entries={lora_quantization_params} bind:params />
				<Accordion class="m-4">
					<AccordionItem>
						<span slot="header">高级</span>
						<ParamGroup
							title="lora量化参数（高级）"
							entries={lora_quantization_advanced}
							bind:params
						/>
					</AccordionItem>
				</Accordion>
			{/if}
	{/if}
	{#if adapter == "p-tuning" || adapter == "prefix-tuning" || adapter == "prompt-tuning"}
		<ParamGroup title="虚拟token参数" entries={num_virt_tokens_param} bind:params />
	{/if}
	<ParamGroup title="训练参数" entries={training_params} bind:params />
	<Accordion class="m-4">
		<AccordionItem>
			<span slot="header">高级</span>
			<ParamGroup title="训练参数（高级）" entries={training_advanced} bind:params />
		</AccordionItem>
	</Accordion>
</div>
