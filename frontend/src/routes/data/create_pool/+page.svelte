<script lang="ts">
  import { StepIndicator, Button, Modal, Hr } from "flowbite-svelte";
  import { Timeline, TimelineItem } from "flowbite-svelte";
  import Information from "./Information.svelte";
  import Dataset from "../DatasetTable.svelte";
  import {
    CalendarWeekOutline,
    CheckCircleOutline,
    AdjustmentsHorizontalOutline,
    AngleLeftOutline,
  } from "flowbite-svelte-icons";
  import { goto } from "$app/navigation";
  import axios from "axios";
  import type FinetuneDatasetEntry from "../../../class/DatasetEntry";
  import type DatasetEntry from "../../../class/DatasetEntry";
  import Uploader from "../Uploader.svelte";
  import { onMount } from "svelte";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");
  let current_step = 1;
  let name = "";
  let description = "";

  let loading = false;
  let pool_id: number = -1;
  if (pool_id == null) {
    loading = true;
  }

  async function create_pool_handle() {
    loading = true;
    const form = new FormData();
    form.append("name", name);
    form.append("description", description);
    pool_id = (
      await axios.post(
        `/api/pool`,
        {},
        {
          params: {
            name: name,
            description: description,
          },
        },
      )
    ).data as number;
    loading = false;
  }

  let stage_empty: boolean;

  const steps = [t("data.task.steps.infor"), t("data.task.steps.upload")];

  const steps_description = [
    t("data.task.steps.infor_des"), t("data.task.steps.upload_des")
  ];

  let next_modal = false;

  function next_handle() {
    if (stage_empty) {
      goto(`/data`);
    } else {
      next_modal = true;
    }
  }

  function return_handle() {
    if (current_step == 1) {
      goto(`/data`);
    } else if (stage_empty) {
      goto(`/data`);
    } else {
      next_modal = true;
    }
  }
</script>

{#if !loading}
  <Modal title="暂存区中仍有未提交的数据" bind:open={next_modal} autoclose>
    <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
      {t("data.task.p1")}
    </p>
    <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
      {t("data.task.p2")}<span class="font-semibold">{t("data.task.p3")}</span>{t("data.task.p4")}
    </p>
    <svelte:fragment slot="footer">
      <div class="w-full flex justify-end gap-2">
        <Button
          color="red"
          on:click={() => {
            goto(`/data`);
          }}>{t("data.task.yes")}</Button
        >
        <Button color="alternative">{t("data.task.no")}</Button>
      </div>
    </svelte:fragment>
  </Modal>

  <ActionPageTitle
    returnTo="/data"
    title={t("data.task.title")}
    subtitle={t("data.task.description")}
  />
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
        {#if current_step == 1}
          <Information bind:name bind:description />
        {:else}
          <Uploader bind:stageEmpty={stage_empty} poolId={pool_id} />
        {/if}
      </div>
      <div class="flex gap-5 m-2 justify-end">
        <div>
          {#if current_step === 2}
            <Button
              on:click={(_) => {
                next_handle();
              }}>{t("data.task.complete")}</Button
            >
          {:else}
            <Button
              disabled={false && (name.length == 0 || description.length == 0)}
              on:click={async (_) => {
                await create_pool_handle();
                ++current_step;
              }}>{t("data.task.title")}</Button
            >
          {/if}
        </div>
      </div>
    </div>
  </div>
{:else}
  <div>loading</div>
{/if}
