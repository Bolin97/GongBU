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
  import Finetuning from "../../components/params/FinetuneParam.svelte";
  import Data from "../../components/Data.svelte";
  import { page } from "$app/stores";
  import { default_finetune_request_params } from "../../../class/FinetuneRequestParams";
  import EvalSelection from "../../components/EvalSelection.svelte";
  import axios from "axios";
  import { goto } from "$app/navigation";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import ModelSelection from "../../components/ModelSelection.svelte";
  import DeviceSelection from "../../components/DeviceSelection.svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");

  let current_step = 1;
  let selected_model_id: string = "";
  let selected_dataset_id: string = "";
  let use_devices: Array<number> | "auto" = [];
  let dir_arr = [];
  let evals = [];
  let name = "";
  let description = "";
  $: output_dir = "/".concat(dir_arr.join("/"));
  let finetune_params = default_finetune_request_params();

  $: {
    finetune_params.devices =
      use_devices == "auto" ? ["auto"] : use_devices.map((x) => x.toString());
    finetune_params.dataset_id = selected_dataset_id.toString();
    finetune_params.model_id = selected_model_id.toString();
    finetune_params.eval_indexes = evals;
  }

  const params = $page.url.searchParams;
  if (params.has("model_id")) {
    selected_model_id = params.get("model_id");
    current_step = 2;
  }

  const steps = [
    t("finetune.model_selection"),
    t("finetune.data_selection"),
    t("finetune.evaluation_metrics"),
    t("finetune.fine_tuning"),
    t("finetune.device_selection"),
    t("finetune.project_name"),
  ];

  const steps_description = [
    t("finetune.choose_model"),
    t("finetune.choose_data"),
    t("finetune.choose_metrics"),
    t("finetune.choose_tuning"),
    t("finetune.choose_device"),
    t("finetune.input_name"),
  ];

  let uploading = false;

  async function submit_handle() {
    uploading = true;
    await axios.post(`/api/finetune`, finetune_params, {
      params: {
        name: name,
        description: description,
      },
    });
    uploading = false;
    goto("/finetune");
  }

  $: device_updater_on = current_step == 5;
</script>

<ActionPageTitle
  title={t("finetune.create_task")}
  subtitle={t("finetune.management")}
  returnTo="/finetune"
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
          <ModelSelection bind:selectedModelId={selected_model_id} />
        </div>
        <div class={`${current_step == 2 ? "" : "hidden"}`}>
          <Data bind:selectedSet={selected_dataset_id} />
        </div>
        <div class={`${current_step == 3 ? "" : "hidden"}`}>
          <EvalSelection bind:indexes={evals} />
        </div>
        <div class={`${current_step == 4 ? "" : "hidden"}`}>
          <Finetuning bind:finetuneParam={finetune_params} />
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
              <span class="font-semibold text-lg m-2"
                >{t("finetune.task_name")}：</span
              >
              <Input
                class="my-2"
                bind:value={name}
                placeholder={t("finetune.enter_task_name")}
              />
            </div>
            <div class="my-4">
              <span class="font-semibold text-lg m-2"
                >{t("finetune.task_description")}：</span
              >
              <Input
                class="my-2"
                bind:value={description}
                placeholder={t("finetune.enter_task_description")}
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
            }}>{t("finetune.complete")}</Button
          >
        {:else if current_step === 5}
          <Button
            disabled={use_devices.length === 0}
            on:click={(_) => ++current_step}>{t("finetune.next_step")}</Button
          >
          {#if use_devices.length === 0}
            <Tooltip>{t("finetune.choose_at_least_one_device")}</Tooltip>
          {/if}
        {:else if current_step == 2}
          <Button
            disabled={selected_dataset_id.length === 0}
            on:click={(_) => ++current_step}>{t("finetune.next_step")}</Button
          >
        {:else if current_step === 1}
          <Button
            disabled={selected_model_id.length === 0}
            on:click={(_) => ++current_step}>{t("finetune.next_step")}</Button
          >
        {:else}
          <Button on:click={(_) => ++current_step}
            >{t("finetune.next_step")}</Button
          >
        {/if}
        <Button
          class={current_step === 1 ? "hidden" : ""}
          on:click={(_) => --current_step}>{t("finetune.previous_step")}</Button
        >
      </div>
    </div>
  </div>
{:else}
  <div>{t("finetune.loading")}</div>
{/if}
