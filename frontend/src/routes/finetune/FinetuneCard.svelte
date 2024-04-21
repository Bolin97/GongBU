<script lang="ts">
  import { getContext } from "svelte";
  import type FinetuneEntry from "../../class/FinetuneEntry";
  import type FinetuneEntryReduced from "../../class/FinetuneEntryReduced";
  import toFormatted from "../../utils/ConvertDatetimeString";
  import FinetuneProgess from "./FinetuneProgess.svelte";

  export let entry: FinetuneEntryReduced;

  const t: any = getContext("t");
</script>

<div
  class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300"
>
  <div class="p-2">
    <div class="tracking-wide text-sm text-blue-600 font-semibold">
      {entry.id} - {entry.name}
    </div>
    <p class="mt-2 text-gray-500">{toFormatted(entry.start_time)}</p>
    <div class="mt-2">
      {#if entry.state == -1}
        <div class="text-xs font-bold">&nbsp;</div>
      {:else}
        <FinetuneProgess id={entry.id.toString()} noUpdate={entry.state == 1} />
      {/if}
    </div>
    <div class="mt-8">
      {#if entry.state == 0}
        {t('finetune.training')}
      {:else if entry.state == 1}
        {t('finetune.training_completed')}
      {:else if entry.state == -1}
        {t('finetune.error')}
      {:else}
        {t('finetune.invalid_status_code')}
      {/if}
    </div>
    <p class="mt-2 text-gray-500">
      {#if entry.description == ""}
      &nbsp;
      {:else}
      {entry.description}
      {/if}
    </p>
    <div class="mt-2">
      <a
        href={`/finetune/details?finetune_id=${entry.id}`}
        class="text-blue-600 hover:underline">{t("finetune.details")}</a
      >
    </div>
  </div>
</div>