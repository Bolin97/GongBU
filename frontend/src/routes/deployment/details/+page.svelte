<script lang="ts">
  import { page } from "$app/stores";
  import { Button, Hr, Modal, Tooltip } from "flowbite-svelte";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import type Deployment from "../../../class/Deployment";
  import { getContext, onDestroy, onMount } from "svelte";
  import axios from "axios";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  import type Adapter from "../../../class/Adapter";
  import { UPDATE_VIEW_INTERVAL } from "../../store";
  import ModelCard from "../../components/ModelCard.svelte";
  import DeviceInfo from "../../components/DeviceInfo.svelte";
  import WrappedIframe from "./WrappedIframe.svelte";
  import { goto } from "$app/navigation";
  import type DatasetEntry from "../../../class/DatasetEntry";
  const t: any = getContext("t");
  const deployment_id = $page.url.searchParams.get("deployment_id");
  let deployment_entry: Deployment = null;
  let base_model: OpenllmEntry = null;
  let adapter: Adapter = null;
  let dataset_entry: DatasetEntry = null;

  async function fetchInfo() {
    deployment_entry = (await axios.get(`/api/deployment/${deployment_id}`))
      .data;
    if (deployment_entry.deploy_base_model) {
      base_model = (
        await axios.get(`/api/openllm/${deployment_entry.model_or_adapter_id}`)
      ).data;
      adapter = null;
    } else {
      adapter = (
        await axios.get(`/api/adapter/${deployment_entry.model_or_adapter_id}`)
      ).data;
      base_model = (
        await axios.get(
          `/api/openllm/entry/by_model_name/${adapter.base_model_name}`,
        )
      ).data;
    }
    
    stopClicked = false;
    startClicked = false;
  }
  let showTooltip = false;
  let tooltipText = 'Copied!';
  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(window.location.origin + `/net/${deployment_entry.port}/openai/v1/chat/completions`);
      showTooltip = true;
      setTimeout(() => {
        showTooltip = false;
      }, 2000);
      console.log('Text copied to clipboard');
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  }
  let updater: any;
  onMount(async () => {
    fetchInfo();
    updater = setInterval(fetchInfo, UPDATE_VIEW_INTERVAL);
  });
  let startClicked = false;
  onDestroy(() => {
    clearInterval(updater);
  });

  async function handleStart() {
    startClicked = true;
    await axios.put(`/api/deployment/start/${deployment_id}`);
    fetchInfo();
  }

  let stopClicked = false;

  async function handleStop() {
    stopClicked = true;
    await axios.put(`/api/deployment/stop/${deployment_id}`);
    fetchInfo();
  }

  let delete_modal = false;
  async function delete_entry_handle() {
    await axios.delete(`/api/deployment/${deployment_id}`);
    goto("/deployment");
  }
</script>

<Modal title={t("deployment.detail.title")} bind:open={delete_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("deployment.detail.delete.p1")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("deployment.detail.delete.p2")}<span class="font-semibold">{t("deployment.detail.delete.p3")}</span>{t("deployment.detail.delete.p4")}
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button
        color="red"
        on:click={() => {
          delete_entry_handle();
        }}>{t("deployment.detail.delete.yes")}</Button
      >
      <Button color="alternative">{t("deployment.detail.delete.no")}</Button>
    </div>
  </svelte:fragment>
</Modal>

{#if base_model != null && deployment_entry != null}
    <ActionPageTitle returnTo="/deployment" title={t("deployment.detail.title")}>
      <svelte:fragment slot="right">
        <div class="flex gap-2">
          {#if (deployment_entry.state == 2 || deployment_entry.state == -1) && !stopClicked}
            <Button color="blue" on:click={handleStop}>{t("deployment.detail.stop")}</Button>
          {/if}
          {#if deployment_entry.state == 0 && !startClicked}
            <Button on:click={handleStart} color="green">{t("deployment.detail.start")}</Button>
          {/if}
          <Button
            color="red"
            on:click={() => {
              delete_modal = true;
            }}
          >
            {t("deployment.detail.delete.yes")}
          </Button>
        </div>
      </svelte:fragment>
    </ActionPageTitle>
    <div class="flex flex-row">
      <div class="w-1/2">
        <div class="p-4 w-full">
          <div
            class="uppercase tracking-wide text-sm text-blue-600 font-semibold"
          >
            {deployment_entry.name}
          </div>
          <p class="mt-2 text-gray-500">{deployment_entry.description}</p>
          <div class="mt-2">
            <span class="text-gray-900 font-bold">{t("deployment.detail.state")}</span>
            <span class="text-gray-600">
              {#if deployment_entry.state == 0}
                {t("deployment.stopped")}
              {:else if deployment_entry.state == 1}
                {t("deployment.starting")}
              {:else if deployment_entry.state == 2}
                {t("deployment.running")}
              {:else}
                {t("deployment.error")}
              {/if}
            </span>
          </div>
          <Hr />
          <div class="mt-2">
            <span class="text-gray-900 font-bold">{t("deployment.detail.gradio_link")}</span>
            <div class="text-sm">
              <p>
                <a
                  href={`/net/${deployment_entry.port}/`}
                  target="_blank"
                  class="text-blue-600 hover:underline"
                >
                  {window.location.origin + `/net/${deployment_entry.port}/`}
                </a>
              </p>
            </div>
          </div>
          <div class="mt-2">
            <span class="text-gray-900 font-bold">{t("deployment.detail.openai_link")}</span>
            <div class="flex flex-row">
              <div class="text-sm">
                <p>
                  <span
                    class="text-blue-600 hover:underline"
                  >
                    {window.location.origin + `/net/${deployment_entry.port}/openai/v1/chat/completions`}
                  </span>
                  
                </p>
              </div>
              <div class="ml-2 flex items-center">
                <svg id=click on:click={copyToClipboard} class="w-6 h-6 text-gray-800 dark:text-white cursor-pointer" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
                  <path fill-rule="evenodd" d="M18 3a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-1V9a4 4 0 0 0-4-4h-3a1.99 1.99 0 0 0-1 .267V5a2 2 0 0 1 2-2h7Z" clip-rule="evenodd"/>
                  <path fill-rule="evenodd" d="M8 7.054V11H4.2a2 2 0 0 1 .281-.432l2.46-2.87A2 2 0 0 1 8 7.054ZM10 7v4a2 2 0 0 1-2 2H4v6a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3Z" clip-rule="evenodd"/>
                </svg>
                <Tooltip trigger="click" triggeredBy="#click" open={showTooltip} placement="top">{tooltipText}</Tooltip>
              </div>
            </div>
          </div>
          <Hr />
          <div class="mt-2">
            <span class="text-gray-900 font-bold">{t("deployment.detail.model")}</span>
            <ModelCard modelId={base_model.id} baseModelNoCursorChange />
          </div>
          {#if adapter != null}
            <div class="mt-2">
              <span class="text-gray-900 font-bold">{t("deployment.detail.adapter")}</span>
              <span class="text-gray-600"
                >{adapter ? adapter.adapter_name : "N/A"}</span
              >
            </div>
          {/if}
          <Hr />
          <div class="mt-2">
            <!-- <div>
              <span class="text-gray-900 font-bold">{t("deployment.detail.deepspeed")} </span>
              <span class="text-gray-600"
                >{deployment_entry.use_deepspeed ? "Yes" : "No"}</span
              >
            </div>
            <div>
              <span class="text-gray-900 font-bold">{t("deployment.detail.flash_attention")}</span>
              <span class="text-gray-600"
                >{deployment_entry.use_flash_attention ? "Yes" : "No"}</span
              >
            </div> -->
            <div>
              <span class="text-gray-900 font-bold">{t("deployment.detail.vllm")}</span>
              <span class="text-gray-600"
                >{deployment_entry.use_vllm ? "Yes" : "No"}</span
              >
            </div>
          </div>
          <Hr />
          <div class="mt-2">
            <span class="text-gray-900 font-bold">{t("deployment.detail.device")}</span>
            <div>
              <DeviceInfo showDevices={deployment_entry.devices} />
            </div>
          </div>
        </div>
      </div>
      <div class="w-1/2 min-h-full">
        <WrappedIframe
          link={`/net/${deployment_entry.port}/`}
          avaliable={deployment_entry.state == 2}
        />
      </div>
    </div>
{/if}
