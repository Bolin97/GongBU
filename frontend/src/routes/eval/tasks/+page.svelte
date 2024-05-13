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
  import Data from "../../components/Data.svelte";
  import { page } from "$app/stores";
  import { ParamType } from "../../components/params/Params";
  import { goto } from "$app/navigation";
  import ParamGroup from "../../components/params/ParamGroup.svelte";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import ModelSelection from "../../components/ModelSelection.svelte";
  import EvalSelection from "../../components/EvalSelection.svelte";
  import DeviceSelection from "../../components/DeviceSelection.svelte";
  import { default_deployment_params } from "../../components/params/Params";
  import DeploymentParam from "../../components/params/DeploymentParam.svelte";
  import { default_deployment_request_params } from "../../../class/DeploymentRequestParams";
  import axios from "axios";
  import { getContext } from "svelte";

  const t: any = getContext("t");

  let current_step = 1;
  let selected_model_id: string = "";
  let selected_adapter_id: string = "";
  let selected_dataset_id: string = "";
  let use_devices: Array<number> | "auto" = [];
  let evals = [];
  let name = "";
  let description = "";

  const params = $page.url.searchParams;
  if (params.has("model_id")) {
    selected_model_id = params.get("model_id");
    current_step = 2;
  }

  const steps = [
    t("eval.steps.model_selection"), 
    t("eval.steps.data_selection"), 
    t("eval.steps.evaluation_metrics"), 
    t("eval.steps.params_selection"), 
    t("eval.steps.device_selection"), 
    t("eval.steps.project_name"), 
  ]

  const steps_description = [
    t("eval.steps.choose_model"), 
    t("eval.steps.choose_data"), 
    t("eval.steps.choose_metrics"), 
    t("eval.steps.choose_params"), 
    t("eval.steps.choose_device"), 
    t("eval.steps.input_name")
  ];

  let uploading = false;

  let deploy_request_params = default_deployment_request_params();
  let val_set_size_params = {
    val_set_size: 1,
  };

  async function submit_handle() {
    uploading = true;
    await axios.post(
      `/api/eval`,
      {
        model_or_adapter_id:
          selected_model_id.length == 0
            ? selected_adapter_id
            : selected_model_id,
        deploy_base_model: selected_adapter_id.length == 0,
        bits_and_bytes: deploy_request_params.bits_and_bytes,
        load_8bit: deploy_request_params.load_8bit,
        load_4bit: deploy_request_params.load_4bit,
        use_flash_attention: deploy_request_params.use_flash_attention,
        use_deepspeed: deploy_request_params.use_deepspeed,
        devices:
          use_devices == "auto"
            ? ["auto"]
            : use_devices.map((x) => x.toString()),
        indexes: evals,
        dataset_id: selected_dataset_id,
        val_set_size: val_set_size_params.val_set_size,
      },
      {
        params: {
          name: name,
          description: description,
        },
      },
    );
    uploading = false;
    goto("/eval");
  }

  $: device_updater_on = current_step == 5;
</script>

<ActionPageTitle
  title={t("eval.task.title")}
  subtitle={t("eval.task.subtitle")}
  returnTo="/eval"
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
          <Data bind:selectedSet={selected_dataset_id} />
          <ParamGroup
            entries={[
              {
                var_name: "val_set_size",
                description: t("eval.eval_size"),
                param_type: ParamType.slider,
                name: t("eval.eval_size"),
                constrains: [
                  { min: 0 },
                  { max: 1 },
                  { step: 0.01 },
                  { values: [0.3, 0.5, 1] },
                ],
              },
            ]}
            title={t("eval.eval_size")}
            bind:params={val_set_size_params}
          />
        </div>
        <div class={`${current_step == 3 ? "" : "hidden"}`}>
          <EvalSelection bind:indexes={evals} />
        </div>
        <div class={`${current_step == 4 ? "" : "hidden"}`}>
          <DeploymentParam
            bind:deploymentParams={deploy_request_params}
            hideParams={["port", "use_vllm"]}
          />
        </div>
        <div class={`${current_step == 5 ? "" : "hidden"}`}>
          <DeviceSelection
            bind:useDevices={use_devices}
            bind:updaterOn={device_updater_on}
          />
        </div>
        <div class={`${current_step == 6 ? "" : "hidden"}`}>
          <div class="m-2 p-2">
            <div class="my-4">
              <span class="font-semibold text-lg m-2">{t("eval.input.task_name")}</span>
              <Input
                class="my-2"
                bind:value={name}
                placeholder={t("eval.input.enter_task_name")}
              />
            </div>
            <div class="my-4">
              <span class="font-semibold text-lg m-2">{t("eval.input.task_description")}</span>
              <Input
                class="my-2"
                bind:value={description}
                placeholder={t("eval.input.enter_task_description")}
              />
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-row-reverse gap-5 m-2">
        {#if current_step === 6}
          <Button
            on:click={(_) => {
              submit_handle();
            }}>{t("eval.task.complete")}</Button
          >
        {:else if current_step === 5}
          <Button
            disabled={use_devices.length === 0}
            on:click={(_) => ++current_step}>{t("eval.task.next_step")}</Button
          >
          {#if use_devices.length === 0}
            <Tooltip>至少选择一个设备</Tooltip>
          {/if}
        {:else if current_step == 2}
          <Button
            disabled={selected_dataset_id.length === 0}
            on:click={(_) => ++current_step}>{t("eval.task.next_step")}</Button
          >
        {:else if current_step === 1}
          <Button
            disabled={selected_model_id.length === 0 &&
              selected_adapter_id.length === 0}
            on:click={(_) => ++current_step}>{t("eval.task.next_step")}</Button
          >
        {:else}
          <Button on:click={(_) => ++current_step}>{t("eval.task.next_step")}</Button>
        {/if}
        <Button
          class={current_step === 1 ? "hidden" : ""}
          on:click={(_) => --current_step}>{t("eval.task.previous_step")}</Button
        >
      </div>
    </div>
  </div>
{:else}
  <div>Loading</div>
{/if}
