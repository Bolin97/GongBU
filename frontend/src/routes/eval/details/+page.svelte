<script lang="ts">
  import { page } from "$app/stores";
  import { Button, Hr, Modal } from "flowbite-svelte";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import type EvalEntry from "../../../class/EvalEntry";
  import { getContext, onDestroy, onMount } from "svelte";
  import axios from "axios";
  import { UPDATE_VIEW_INTERVAL } from "../../store";
  import { goto } from "$app/navigation";
  import ModelCard from "../../components/ModelCard.svelte";
  import type Adapter from "../../../class/Adapter";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  import { PlusOutline } from "flowbite-svelte-icons";
  const t: any = getContext("t");
  const eval_id = $page.url.searchParams.get("eval_id");
  let eval_entry: EvalEntry = null;
  let adapter_name: string = null;
  let dataset_entry: DatasetEntry = null;

  async function fetchInfo() {
    eval_entry = (await axios.get(`/api/eval/${eval_id}`)).data;
    if (eval_entry.deploy_base_model) {
      base_model = eval_entry.model_or_adapter_id;
    } else {
      const adapter = (
        await axios.get(`/api/adapter/${eval_entry.model_or_adapter_id}`)
      ).data as Adapter;
      const base_model_name = adapter.base_model_name;
      adapter_name = adapter.adapter_name;
      base_model = (
        (await axios.get(`/api/openllm/entry/by_model_name/${base_model_name}`))
          .data as OpenllmEntry
      ).id;
    }
    dataset_entry = (
      await axios.get(`/api/dataset_entry/${eval_entry.dataset_id}`)
    ).data as DatasetEntry;
    console.log(dataset_entry)
  }
  let updater: any;
  onMount(async () => {
    fetchInfo();
    updater = setInterval(fetchInfo, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(updater);
  });

  let delete_modal = false;
  let base_model = null;
  async function delete_entry_handle() {
    await axios.delete(`/api/eval/${eval_id}`);
    goto("/eval");
  }

  $: eval_results =
    eval_entry && eval_entry.result != undefined && eval_entry.result != null
      ? Object.entries(eval_entry.result).map(([key, value]) => ({
          name: key,
          value: value,
        }))
      : [];
  $: console.log(eval_results)
  import { eval_index_full_name } from "../../shared";
  import type DatasetEntry from "../../../class/DatasetEntry";
  import EvalProgress from "../EvalProgress.svelte";
</script>

<Modal title={t("eval.detail.delete.title")} bind:open={delete_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("eval.detail.delete.p1")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("eval.detail.delete.p2")}<span
      class="font-semibold">{t("eval.detail.delete.p3")}</span
    >.
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button color="red" on:click={delete_entry_handle}>Delete</Button>
      <Button color="alternative">No</Button>
    </div>
  </svelte:fragment>
</Modal>

{#if eval_entry != null && base_model != null && dataset_entry != null}
  <ActionPageTitle returnTo="/eval" title={t("eval.detail.title")}>
    <svelte:fragment slot="right">
      <div class="flex gap-2">
        <Button
          color="red"
          on:click={() => {
            delete_modal = true;
          }}
        >
          {t("eval.detail.delete.delete")}
        </Button>
      </div>
    </svelte:fragment>
  </ActionPageTitle>
  <div class="flex flex-row w-full">
    <div class="p-4 w-1/2">
      <div class="uppercase tracking-wide text-sm text-blue-600 font-semibold">
        {eval_entry.name}
      </div>
      <p class="mt-2 text-gray-500">{eval_entry.description}</p>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.state")}</span>
        <span class="text-gray-600">
          {#if eval_entry.state == 0}
            {t("eval.detail.loading_model")}
          {:else if eval_entry.state == 1}
            {t("eval.detail.starting")}
          {:else if eval_entry.state == 2}
            {t("eval.detail.generating")}
          {:else if eval_entry.state == 3}
            {t("eval.detail.evaluating")}
          {:else if eval_entry.state == 4}
            {t("eval.detail.done")}
          {:else if eval_entry.state == -1}
            {t("eval.error")}
          {/if}
        </span>
      </div>
      {#if eval_entry.state == 2}
      <div class="my-2 mb-6">
        <EvalProgress id={eval_id} />
      </div>
      {/if}
      <div class="mt-2">
        <ModelCard modelId={base_model} baseModelNoCursorChange />
        {#if !eval_entry.deploy_base_model}
          <span class="text-gray-900 font-bold">{t("eval.detail.adapter")}</span>
          <span class="text-gray-600">{adapter_name}</span>
        {/if}
      </div>
      <hr class="my-2" />
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.dataset_name")}</span>
        <span class="text-gray-600">{dataset_entry.name}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.dataset_des")}</span>
        <span class="text-gray-600">{dataset_entry.description}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.dataset_size")} </span>
        <span class="text-gray-600">{dataset_entry.size}</span>
      </div>
      <hr class="my-2" />
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.bits_and_bytes")}</span>
        <span class="text-gray-600"
          >{eval_entry.bits_and_bytes ? "Yes" : "No"}</span
        >
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.val_set_size")}</span>
        <span class="text-gray-600">{eval_entry.val_set_size}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">{t("eval.detail.use_deepspeed")}</span>
        <span class="text-gray-600"
          >{eval_entry.use_deepspeed ? "Yes" : "No"}</span
        >
      </div>
    </div>
    <div class="p-4 w-1/3">
      {#if eval_entry.state == 4 && eval_results != null && eval_results != undefined}
        <div class="bg-white shadow overflow-hidden sm:rounded-lg">
          {#each eval_results as result}
            <div
              class="px-4 py-5 sm:px-6 flex justify-between border-t border-gray-200"
            >
              <h1 class="text-lg leading-6 font-medium text-gray-900">
                {eval_index_full_name[result.name]}
              </h1>
              <span class="mt-1 max-w-2xl text-sm text-gray-500"
                >{result.value}</span
              >
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}
