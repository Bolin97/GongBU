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
  import { eval_index_full_name } from "../../shared";
</script>

<Modal title="Confirm Deletion" bind:open={delete_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    Are you sure you want to delete?
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    After deletion, all related information of this task will be <span
      class="font-semibold">irrecoverable</span
    >.
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button color="red" on:click={delete_entry_handle}>Delete</Button>
      <Button color="alternative">No</Button>
    </div>
  </svelte:fragment>
</Modal>

{#if eval_entry != null && base_model != null}
  <ActionPageTitle returnTo="/eval" title="Detailed Information">
    <svelte:fragment slot="right">
      <div class="flex gap-2">
        <Button
          color="red"
          on:click={() => {
            delete_modal = true;
          }}
        >
          Delete
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
        <span class="text-gray-900 font-bold">State: </span>
        <span class="text-gray-600">
          {eval_entry.state}
        </span>
      </div>
      <div class="mt-2">
        <ModelCard modelId={base_model} baseModelNoCursorChange />
        {#if !eval_entry.deploy_base_model}
          <span class="text-gray-900 font-bold">Adapter: </span>
          <span class="text-gray-600">{adapter_name}</span>
        {/if}
      </div>
      <hr class="my-2" />
      <div class="mt-2">
        <span class="text-gray-900 font-bold">Dataset ID: </span>
        <span class="text-gray-600">{eval_entry.dataset_id}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">Bits and Bytes: </span>
        <span class="text-gray-600"
          >{eval_entry.bits_and_bytes ? "Yes" : "No"}</span
        >
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">Val Set Size: </span>
        <span class="text-gray-600">{eval_entry.val_set_size}</span>
      </div>
      <div class="mt-2">
        <span class="text-gray-900 font-bold">Use Deepspeed: </span>
        <span class="text-gray-600"
          >{eval_entry.use_deepspeed ? "Yes" : "No"}</span
        >
      </div>
    </div>
    <div class="p-4 w-1/3">
      {#if eval_entry.state == 3 && eval_results != null && eval_results != undefined}
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
