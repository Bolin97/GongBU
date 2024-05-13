<script lang="ts">
  import { Accordion, AccordionItem } from "flowbite-svelte";
  import type EvalEntry from "../../class/EvalEntry";
  import toFormatted from "../../utils/ConvertDatetimeString";
  import EvalProgress from "./EvalProgress.svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");

  export let evalEntry: EvalEntry;
</script>

<div
  class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300"
>
  <div class="p-2">
    <div class="tracking-wide text-sm text-blue-600 font-semibold">
      {evalEntry.id} - {evalEntry.name}
    </div>
    <p class="mt-2 text-gray-500">
      {toFormatted(evalEntry.start_time)} -- {evalEntry.end_time
        ? toFormatted(evalEntry.end_time)
        : t("eval.detail.running")}
    </p>
    <p class="mt-2 text-gray-500">
      {evalEntry.description}
      {#if evalEntry.description == ""}
        &nbsp;
      {/if}
    </p>
    <div class="mt-2">
      <a
        href={`/eval/details?eval_id=${evalEntry.id}`}
        class="text-blue-600 hover:underline">{t("eval.detail.title")}</a
      >
    </div>
    {#if evalEntry.state == 2}
      <EvalProgress id={evalEntry.id.toString()} />
    {/if}
  </div>
</div>
