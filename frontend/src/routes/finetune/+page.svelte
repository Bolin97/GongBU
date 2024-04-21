<script lang="ts">
  import { Button } from "flowbite-svelte";
  import type FinetuneEntry from "../../class/FinetuneEntry";
  import { getContext, onDestroy, onMount } from "svelte";
  import axios from "axios";
  import { PlusOutline } from "flowbite-svelte-icons";
  import { UPDATE_VIEW_INTERVAL } from "../store";
  import FinetuneProgess from "./FinetuneProgess.svelte";
  import { page } from "$app/stores";
  import toFormatted from "../../utils/ConvertDatetimeString";
  import type FinetuneEntryReduced from "../../class/FinetuneEntryReduced";
  import FinetuneCard from "./FinetuneCard.svelte";
  import ActionPageTitle from "../components/ActionPageTitle.svelte";
  const t: any = getContext("t");

  let entries = [] as Array<FinetuneEntryReduced>;

  let entries_updater: any;
  onMount(async () => {
    async function update() {
      entries = (await axios.get(`/api/finetune_entry/reduced`))
        .data as Array<FinetuneEntryReduced>;
    }
    update();
    entries_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(entries_updater);
  });
</script>

<ActionPageTitle title={t('finetune.management')} subtitle={t('finetune.finetune')}>
  <svelte:fragment slot="right">
    <Button href="/finetune/tasks">
      <PlusOutline />
      {t('finetune.create_task')}
    </Button>
  </svelte:fragment>
</ActionPageTitle>

<hr class="pt-1" />
<div class="grid grid-cols-3">
  {#each entries as entry}
    <div class="mx-4 my-2">
      <FinetuneCard {entry} />
    </div>
  {/each}
</div>