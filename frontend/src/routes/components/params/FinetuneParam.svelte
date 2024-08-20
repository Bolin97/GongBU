<script lang="ts">
  import {
    Radio,
    Label,
    Input,
    Hr,
    Accordion,
    AccordionItem,
    Button,
  } from "flowbite-svelte";
  import ParamGroup from "./ParamGroup.svelte";
  import {
    type ParamEntry,
    ParamType,
    param_component_mapper,
    default_finetune_params,
    num_virt_tokens_param,
    lora_quantization_params,
    lora_quantization_advanced,
    training_params,
    training_advanced,
  } from "./Params";
  import type { FinetuneRequestParams } from "../../../class/FinetuneRequestParams";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  const adapters: Array<
    | "lora"
    | "qlora"
    | "adalora"
    | "p-tuning"
    | "prefix-tuning"
    | "prompt-tuning"
    | "IA3"
    | "lokr"
    | "loha"
    | "lomo"
    | "galore"
  > = [
    "lora",
    "qlora",
    "adalora",
    "p-tuning",
    "prefix-tuning",
    "prompt-tuning",
    "IA3",
    "lokr",
    "loha",
    "lomo",
    "galore"
  ];
  import { lora_specific_params } from "./Params";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  let adapter = "lora";
  let params = default_finetune_params();
  export let finetuneParam: FinetuneRequestParams;
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
  }

</script>

<div>
  <div class="flex flex-row gap-2 m-2 my-10">
    <span>{t("finetune.finetune_params.finetune_method_select")}</span>
    {#each adapters as adapter_name}
      <Radio bind:group={adapter} name="method" value={adapter_name}
        ><p class="text-lg">{adapter_name}</p></Radio
      >
    {/each}
  </div>
  {#if adapter == "lora" || adapter == "qlora" || adapter == "adalora" || adapter == "lokr" || adapter == "loha"}
    <ParamGroup title={t("finetune.finetune_params.lora_params.title")} entries={lora_specific_params} bind:params />
    {#if adapter == "qlora"}
      <ParamGroup
        title={t("finetune.finetune_params.qlora_params.title")}
        entries={lora_quantization_params}
        bind:params
      />
      <Accordion class="m-4">
        <AccordionItem>
          <span slot="header">{t("finetune.finetune_params.qlora_params.advanced_options_title")}</span>
          <ParamGroup
            title={t("finetune.finetune_params.qlora_params.q_params_ad")}
            entries={lora_quantization_advanced}
            bind:params
          />
        </AccordionItem>
      </Accordion>
    {/if}
  {/if}
  {#if adapter == "p-tuning" || adapter == "prefix-tuning" || adapter == "prompt-tuning"}
    <ParamGroup
      title={t("finetune.finetune_params.p_params.title")}
      entries={num_virt_tokens_param}
      bind:params
    />
  {/if}
  <ParamGroup title={t("finetune.finetune_params.train_params.title")} entries={training_params} bind:params />
  <Accordion class="m-4">
    <AccordionItem>
      <span slot="header">{t("finetune.finetune_params.train_params.advanced_options_title")}</span>
      <ParamGroup
        title={t("finetune.finetune_params.train_params.train_params_ad")}
        entries={training_advanced}
        bind:params
      />
    </AccordionItem>
  </Accordion>
</div>
