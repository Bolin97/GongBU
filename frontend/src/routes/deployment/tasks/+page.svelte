<script lang="ts">
  import {
    StepIndicator,
    Button,
    Label,
    Input,
    Tooltip,
    Hr,
  } from "flowbite-svelte";
  import { Timeline, TimelineItem } from "flowbite-svelte";
  import {
    CalendarWeekOutline,
    CheckCircleOutline,
    AdjustmentsHorizontalOutline,
    AngleLeftOutline,
  } from "flowbite-svelte-icons";
  import Device from "./Device.svelte";
  import { page } from "$app/stores";
  import axios from "axios";
  import { goto } from "$app/navigation";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import ModelSelection from "../../components/ModelSelection.svelte";
  import {
    default_deployment_request_params,
    type DeploymentRequestParams,
  } from "../../../class/DeploymentRequestParams";
  import Deployment from "../../components/params/DeploymentParam.svelte";
  let current_step = 1;
  let selected_model_id: string = "";
  let selected_adapter_id: string = "";
  let use_devices: Array<number> | "auto" = [];
  let name = "";
  let description = "";

  let model_entry: OpenllmEntry = {
    id: "",
    model_name: "",
    model_description: "",
    view_pic: "",
    remote_path: "",
    local_path: "",
    local_store: 0,
    storage_state: "",
    storage_date: "",
    display_name: "",
    owner: "",
    public: false,
  };
  import { getContext } from "svelte";
  import type Adapter from "../../../class/Adapter";
  const t: any = getContext("t");

  $: {
    if (current_step == 2) {
      axios.get(`/api/openllm/${selected_model_id}`).then((res) => {
        model_entry = res.data;
      });
    }
  }

  let show_use_vllm = false;
  $: (async () => {
    if(selected_adapter_id.length == 0) {
      show_use_vllm = true;
      return;
    }
    const adapter_info: Adapter = (await axios.get(
      `/api/adapter/${selected_adapter_id}`
    )).data
    const ft_entry = (await axios.get(
      `/api/finetune_entry/${adapter_info.ft_entry}`
    )).data;
    show_use_vllm = ft_entry.adapter_name == "lora";
  })();
  let deployment_request_params: DeploymentRequestParams =
    default_deployment_request_params();
  $: {
    deployment_request_params.devices =
      use_devices == "auto" ? ["auto"] : use_devices.map((x) => x.toString());
    deployment_request_params.model_or_adpater_id =
      selected_model_id.length > 0
        ? Number.parseInt(selected_model_id)
        : Number.parseFloat(selected_adapter_id);
    deployment_request_params.deploy_base_model = selected_model_id.length > 0;
  }

  const params = $page.url.searchParams;
  if (params.has("model_id")) {
    selected_model_id = params.get("model_id");
    current_step = 2;
  }

  const steps = [
    t("deployment.task.steps.model"), 
    t("deployment.task.steps.device"), 
    t("deployment.task.steps.params"), 
    t("deployment.task.steps.name")];

  const steps_description = [
    t("deployment.task.steps.model_des"), 
    t("deployment.task.steps.device_des"), 
    t("deployment.task.steps.params_des"), 
    t("deployment.task.steps.name_des")
  ];

  let uploading = false;

  async function submit_handle() {
    uploading = true;
    await axios.post(`/api/deployment`, deployment_request_params, {
      params: {
        name: name,
        description: description,
      },
    });
    uploading = false;
    goto("/deployment");
  }

  const searchParams = $page.url.searchParams;
  if (searchParams.get("adapter_id") || searchParams.get("model_id")) {
    selected_adapter_id = searchParams.get("adapter_id");
    selected_model_id = searchParams.get("model_id");
    current_step = 2;
  }

  $: device_updater_on = current_step == 1;
</script>

<ActionPageTitle
  title={t("deployment.task.title")}
  subtitle={t("deployment.task.des")}
  returnTo="/deployment"
/>
{#if !uploading}
  <div class="w-full flex flex-row p-1 m-2 mt-4">
    <div>
      <Timeline order="vertical">
        {#each steps as step, i}
          <TimelineItem title={step} date="">
            <svelte:fragment slot="icon">
              <span
                class="flex absolute -left-3 justify-center items-center w-6 h-6 bg-primary-200 rounded-full ring-8 ring-white dark:ring-gray-900 dark:bg-primary-900"
              >
                {#if i + 1 === current_step}
                  <AdjustmentsHorizontalOutline
                    size="sm"
                    class="text-primary-500 dark:text-primary-400"
                  />
                {:else if i + 1 < current_step}
                  <CheckCircleOutline
                    size="sm"
                    class="text-primary-500 dark:text-primary-400"
                  />
                {:else}
                  <CalendarWeekOutline
                    size="sm"
                    class="text-primary-500 dark:text-primary-400"
                  />
                {/if}
              </span>
            </svelte:fragment>
            <p
              class="mb-4 text-base font-normal text-gray-500 dark:text-gray-400"
            >
              {steps_description[i]}
            </p>
          </TimelineItem>
        {/each}
      </Timeline>
    </div>
    <div class="w-full m-2">
      <StepIndicator currentStep={current_step} {steps} color="blue" />
      <div>
        <div class={`${current_step == 1 ? "" : "hidden"}`}>
          <ModelSelection
            bind:selectedModelId={selected_model_id}
            bind:selectedAdapterId={selected_adapter_id}
            enableAdapterSelection
          />
        </div>
        <div class={`${current_step == 2 ? "" : "hidden"}`}>
          <Device
            bind:useDevices={use_devices}
            bind:updaterOn={device_updater_on}
          />
        </div>
        <div class={`${current_step == 3 ? "" : "hidden"}`}>
          <Deployment bind:deploymentParams={deployment_request_params}
          hideParams={
            show_use_vllm ? [] : ['use_vllm']
          }/>
        </div>
        <div class={`${current_step == 4 ? "" : "hidden"}`}>
          <div class="m-2 p-2">
            <div class="my-4">
              <span class="font-semibold text-lg m-2">{t("deployment.task.task_name")}</span>
              <Input
                class="my-2"
                bind:value={name}
                placeholder={t("deployment.task.enter_task_name")}
              />
            </div>
            <div class="my-4">
              <span class="font-semibold text-lg m-2">{t("deployment.task.task_description")}</span>
              <Input
                class="my-2"
                bind:value={description}
                placeholder={t("deployment.task.enter_task_description")}
              />
            </div>
          </div>
        </div>
      </div>
      <div class="flex flex-row-reverse gap-5 m-2">
        {#if current_step === 4}
          <Button
            on:click={(_) => {
              submit_handle();
            }}>{t("deployment.task.complete")}</Button
          >
        {:else if current_step == 1}
          <Button
            disabled={selected_adapter_id.length == 0 &&
              selected_model_id.length == 0}
            on:click={(_) => ++current_step}>{t("deployment.task.next_step")}</Button
          >
        {:else if current_step == 2}
          <Button
            disabled={use_devices.length == 0}
            on:click={(_) => ++current_step}>{t("deployment.task.next_step")}</Button
          >
        {:else}
          <Button on:click={(_) => ++current_step}>{t("deployment.task.next_step")}</Button>
        {/if}
        <Button
          class={current_step === 1 ? "hidden" : ""}
          on:click={(_) => --current_step}>{t("deployment.task.previous_step")}</Button
        >
      </div>
    </div>
  </div>
{:else}
  <div>Loading</div>
{/if}
