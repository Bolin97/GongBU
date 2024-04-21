<script lang="ts">
  import type OpenllmEntry from "../../class/OpenllmEntry";
  import { getContext, onMount } from "svelte";
  import { goto } from "$app/navigation";
  import axios from "axios";
  import ModelCard from "../components/ModelCard.svelte";
  import VisbilityButton from "../components/VisbilityButton.svelte";
  let models = [] as Array<OpenllmEntry>;
  onMount(async () => {
    models = (await axios.get(`/api/openllm`)).data;
  });
  const t: any = getContext("t");
</script>

<div class="pt-2 w-full">
  <span class="text-2xl pt-1 text-black-400 font-bold"
    >&nbsp;&nbsp;模型广场</span
  >
  <span class="text-1xl pt-2 text-black-400 text-center"
    >&nbsp;&nbsp;集中展示与管理预置开源大模型，支持对模型进行微调与部署</span
  >
</div>
<hr class="pt-1" />

{#if models.length != 0}
  <div class="grid grid-cols-2">
    {#each models as model}
      <div class="mx-4 my-2">
        <ModelCard
          modelId={model.id}
          showAdapters
          adapterAction
          baseModelNoCursorChange
          adapterNoCursorChange
        >
          <svelte:fragment slot="base-action">
            <button
              on:click={(_) => goto(`/finetune/tasks?model_id=${model.id}`)}
              type="button"
              class="text-white bg-[#1da1f2] hover:bg-[#1da1f2]/90 focus:ring-4 focus:outline-none focus:ring-[#1da1f2]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#1da1f2]/55 me-2 mb-2"
            >
              {t("model.finetune")}
            </button>
            <button
              on:click={(_) => goto(`/deployment/tasks?model_id=${model.id}`)}
              type="button"
              class="text-white bg-[#4285F4] hover:bg-[#4285F4]/90 focus:ring-4 focus:outline-none focus:ring-[#4285F4]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#4285F4]/55 me-2 mb-2"
            >
              {t("model.deploy")}
            </button>
            <VisbilityButton id={model.id} asset="openllm" interactStyle="button" />
          </svelte:fragment>
          <svelte:fragment slot="adapter-action" let:adapter>
            <button
              on:click={(_) =>
                goto(
                  `/deployment/tasks?model_id=${model.id}&adapter_id=${adapter.id}`,
                )}
              type="button"
              class="mx-1 text-blue-600 hover:underline"
            >
              {t("model.deploy")}
            </button>
            <VisbilityButton id={adapter.id} asset="adapter" interactStyle="link" />
          </svelte:fragment>
        </ModelCard>
      </div>
    {/each}
  </div>
{/if}
