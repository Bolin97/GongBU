<script lang="ts">
  import {
    Button,
    Hr,
    Label,
    Tooltip,
    Toast,
    Accordion,
    AccordionItem,
    Modal,
    Checkbox,
    Toggle,
    Progressbar,
  } from "flowbite-svelte";
  import { AngleLeftOutline } from "flowbite-svelte-icons";
  import { page } from "$app/stores";
  import { onDestroy, onMount } from "svelte";
  import axios from "axios";
  import type LoggingRecord from "../../../class/LoggingRecord";
  import { UPDATE_VIEW_INTERVAL } from "../../store";
  import type OpenllmEntry from "../../../class/OpenllmEntry";
  import type FinetuneEntry from "../../../class/FinetuneEntry";
  import {
    lora_specific_params,
    lora_quantization_params,
    lora_quantization_advanced,
    num_virt_tokens_param,
    training_params,
    training_advanced,
    type ParamEntry,
  } from "../../components/params/Params";
  import FinetuneProgess from "../FinetuneProgess.svelte";
  import { goto } from "$app/navigation";
  import type EvalRecord from "../../../class/EvalRecord";
  import Charts from "./Charts.svelte";
  import type FinetuneEntryReduced from "../../../class/FinetuneEntryReduced";
  import { REALTIME_FINETUNE_DETAIL } from "../../store";
  import type CudaDeviceEntry from "../../../class/CudaDeviceEntry";
  import type DatasetEntry from "../../../class/DatasetEntry";
  import GoBack from "../../components/GoBack.svelte";
  import ModelCard from "../../components/ModelCard.svelte";
  import DeviceInfo from "../../components/DeviceInfo.svelte";
  import ActionPageTitle from "../../components/ActionPageTitle.svelte";
  import { getContext } from "svelte";
  const t: any = getContext("t");

  let real_time_toggle = $REALTIME_FINETUNE_DETAIL;
  $: {
    $REALTIME_FINETUNE_DETAIL = real_time_toggle;
  }
  let real_time = false;
  REALTIME_FINETUNE_DETAIL.subscribe((v) => {
    real_time = v;
  });
  const id = $page.url.searchParams.get("finetune_id");
  // const id = "2"
  let finetune_entry: FinetuneEntry;
  let model_entry: OpenllmEntry;

  let finetune_entry_updater: any;
  let dataset_entry: DatasetEntry;
  onMount(async () => {
    async function update() {
      if (finetune_entry.state == 0) {
        const reduced_entry = (
          await axios.get(`/api/finetune_entry/reduced/${id}`)
        ).data as FinetuneEntryReduced;
        if (reduced_entry.state == 1) {
          setTimeout(() => {
            finetune_entry.state = reduced_entry.state;
          }, UPDATE_VIEW_INTERVAL * 2);
        } else {
          finetune_entry.state = reduced_entry.state;
        }
      }
    }
    finetune_entry = (await axios.get(`/api/finetune_entry/${id}`)).data;
    model_entry = (await axios.get(`/api/openllm/${finetune_entry.model_id}`))
      .data;
    dataset_entry = (
      await axios.get(`/api/dataset_entry/${finetune_entry.dataset_id}`)
    ).data;
    finetune_entry_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(finetune_entry_updater);
  });

  interface ParamGroup {
    title: string;
    advanced: boolean;
    params: Array<{
      name: string;
      value: string;
    }>;
  }

  let groups: Array<ParamGroup> = [];
  let adapter_name: string = "";

  function parse_into_param_groups(entry: FinetuneEntry) {
    return {
      lora_specific_params: {
        title: t("finetune.finetune_params.lora_params.title"),
        advanced: false,
        params: lora_specific_params.map((entry) => {
          return {
            name: entry.var_name,
            value: finetune_entry[entry.var_name],
          };
        }),
      },
      lora_quantization_params: {
        title: t("finetune.finetune_params.qlora_params.title"),
        advanced: false,
        params: [
          {
            name: lora_quantization_params[0].var_name,
            value: finetune_entry.load_4bit ? "4" : "8",
          },
        ],
      },
      lora_quantization_advanced: {
        title: t("finetune.finetune_params.qlora_params.q_params_ad"),
        advanced: true,
        params: lora_quantization_advanced.map((entry) => {
          return {
            name: entry.var_name,
            value: finetune_entry[entry.var_name],
          };
        }),
      },
      num_virt_tokens_param: {
        title: t("finetune.finetune_params.p_params.title"),
        advanced: false,
        params: num_virt_tokens_param.map((entry) => {
          return {
            name: entry.var_name,
            value: finetune_entry[entry.var_name],
          };
        }),
      },
      train_params: {
        title: t("finetune.finetune_params.train_params.title"),
        advanced: false,
        params: training_params.map((entry) => {
          return {
            name: entry.var_name,
            value: finetune_entry[entry.var_name],
          };
        }),
      },
      training_advanced: {
        title: t("finetune.finetune_params.train_params.train_params_ad"),
        advanced: true,
        params: training_advanced.map((entry) => {
          return {
            name: entry.var_name,
            value: finetune_entry[entry.var_name],
          };
        }),
      },
    };
  }

  $: {
    if (finetune_entry != undefined) {
      const g = parse_into_param_groups(finetune_entry);
      if (
        finetune_entry.adapter_name == "lora" &&
        !finetune_entry.bits_and_bytes
      ) {
        groups = [g.lora_specific_params, g.train_params, g.training_advanced];
        adapter_name = "lora";
      } else if (
        finetune_entry.adapter_name == "lora" &&
        finetune_entry.bits_and_bytes
      ) {
        groups = [
          g.lora_specific_params,
          g.lora_quantization_params,
          g.train_params,
          g.lora_quantization_advanced,
          g.training_advanced,
        ];
        adapter_name = "qlora";
      } else {
        adapter_name = finetune_entry.adapter_name;
        groups =
          finetune_entry.adapter_name.toLowerCase() == "IA3"
            ? []
            : [g.num_virt_tokens_param];
        groups = groups.concat([g.train_params, g.training_advanced]);
      }
    }
  }

  let delete_modal = false;
  let double_check = false;

  async function delete_entry_handle() {
    await axios.delete(`/api/finetune_entry/${id}`);
    goto("/finetune");
  }

  let stop_modal = false;

  async function stop_handle() {
    axios.put(`/api/finetune/stop/${id}`);
  }
</script>

<Modal title={t("finetune.detail.interrupt.title")} bind:open={stop_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("finetune.detail.interrupt.p1")}
  </p>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("finetune.detail.interrupt.p2")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("finetune.detail.interrupt.p3")}<span class="font-bold">{t("finetune.detail.interrupt.p4")}</span>{t("finetune.detail.interrupt.p5")}
  </p>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button
        color="red"
        on:click={() => {
          stop_handle();
        }}>{t("finetune.detail.yes")}</Button
      >
      <Button color="alternative">{t("finetune.detail.no")}</Button>
    </div>
  </svelte:fragment>
</Modal>

<Modal title={t("finetune.detail.delete.title")} bind:open={delete_modal} autoclose>
  <p class="text-base leading-relaxed text-gray-500 dark:text-gray-400">
    {t("finetune.detail.delete.p1")}
  </p>
  <p class="text-base leading-relaxed text-red-600 dark:text-gray-400">
    {t("finetune.detail.delete.p2")}<span class="font-semibold">{t("finetune.detail.delete.p3")}</span>{t("finetune.detail.delete.p4")}
  </p>
  <div class="flex flex-row justify-end p-2 m-2 align-middle items-center">
    {t("finetune.detail.delete.p5")}<span class="font-semibold text-red-600">{t("finetune.detail.delete.p6")}</span
    >{t("finetune.detail.delete.p7")}
    <Checkbox class="mx-2" bind:checked={double_check} />
  </div>
  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">
      <Button
        disabled={!double_check}
        color="red"
        on:click={() => {
          delete_entry_handle();
        }}>{t("finetune.detail.yes")}</Button
      >
      <Button color="alternative">{t("finetune.detail.no")}</Button>
    </div>
  </svelte:fragment>
</Modal>

{#if finetune_entry == undefined || dataset_entry == undefined || model_entry == undefined}
  loading
{:else}
  <div>
    <ActionPageTitle returnTo="/finetune" title={t("finetune.detail.title")}>
      <svelte:fragment slot="left">
        <div class="flex flex-row mx-2 p-2">
          <span class="mx-2">{t("finetune.detail.real_time_data")}</span>
          <Toggle bind:checked={real_time_toggle} />
        </div>
      </svelte:fragment>
      <svelte:fragment slot="right">
        <div class="flex gap-2">
          <Button
            color="red"
            class={`${finetune_entry.state == 0 ? "" : "hidden"}`}
            on:click={(_) => {
              stop_modal = true;
            }}>{t("finetune.detail.interrupt.interrupt")}</Button
          >
          <Button
            href="/deployment/tasks"
            class={`${finetune_entry.state == 1 ? "" : "hidden"}`}
            color="blue">{t("finetune.detail.deployment")}</Button
          >
          <Button
            on:click={(_) => {
              delete_modal = true;
            }}
            color="red"
            >
            <!-- class={`${finetune_entry.state != 0 ? "" : "hidden"}`} -->
          {t("finetune.detail.delete.title")}
          </Button>
        </div>
      </svelte:fragment>
    </ActionPageTitle>
    <div class="flex flex-row">
      <div class="flex flex-col w-1/2">
        <div class="m-4">
          <div class="flex flex-row mb-1 items-center w-full">
            <span class="text-1xl pt-1 text-black-400 font-bold">{t("finetune.model")}:</span>
            <div class="pl-2 w-[80%]">
              {#if finetune_entry.state == 0}
                <div class="flex flex-row w-full">
                  <Button class="cursor-default" color="blue">{t("finetune.training")}</Button>
                  <div class="m-2 p-2 w-[50%]">
                    <FinetuneProgess {id} />
                  </div>
                </div>
              {:else if finetune_entry.state == 1}
                <Button class="cursor-default" color="green">{t("finetune.training_completed")}</Button>
              {:else if finetune_entry.state == -1}
                <Button class="cursor-default" color="red">{t("finetune.error")}</Button>
              {:else}
                {t("finetune.invalid_status_code")}
              {/if}
            </div>
          </div>
          <div class="p-1">
            {#if model_entry === undefined}
              <div
                class="flex w-74 items-center px-5 bg-white border border-gray-200 rounded-lg shadow dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700"
              >
                loading...
              </div>
            {:else}
              <ModelCard modelId={model_entry.id} baseModelNoCursorChange />
            {/if}
          </div>
        </div>
        <Hr />
        <div class="grid gap-2 m-4 grid-cols-1 lg:grid-cols-2">
          <div>
            <Label for="first_name" class="mb-2">
              {t("finetune.detail.method")}{adapter_name}
            </Label>
          </div>
        </div>
        {#each groups.filter((g) => {
          return !g.advanced;
        }) as group}
          <Hr />
          <div class="m-1">
            <span class="text-1xl pt-1 text-black-400 font-bold"
              >{group.title}</span
            >
            <div class="grid gap-2 m-2 grid-cols-1 lg:grid-cols-2">
              {#each group.params as param}
                <div>
                  <Label for="first_name" class="mb-2">
                    {param.name}: {param.value}
                  </Label>
                </div>
              {/each}
            </div>
          </div>
        {/each}
        <Hr />
        <div class="m-1">
          <span class="text-1xl pt-1 text-black-400 font-bold"
            >{t("finetune.detail.device")}</span
          >
          <div class="gap-2 m-1 grid grid-cols-1 lg:grid-cols-2">
            <DeviceInfo showDevices={finetune_entry.devices} />
          </div>
        </div>
        <Hr />
        <div class="m-1">
          <span class="text-1xl pt-1 text-black-400 font-bold">{t("finetune.detail.data")}</span>
          <div class="m-1">
            <div>{dataset_entry.name}</div>
            <div class="mt-1 p-2 text-sm text-gray-800">
              {dataset_entry.description}
            </div>
          </div>
        </div>
        <Hr />
        <div class="m-1">
          <span class="text-1xl pt-1 text-black-400 font-bold">{t("finetune.detail.save_path")}</span>
          <div class="flex flex-row gap-2 m-1">
            <Label class="mb-2">
              {finetune_entry.output_dir}
            </Label>
          </div>
        </div>
        <Accordion>
          <AccordionItem>
            <span slot="header">{t("finetune.detail.advanced")}</span>
            {#each groups.filter((g) => {
              return g.advanced;
            }) as group, index}
              <div class="m-1">
                <span class="text-1xl pt-1 text-black-400 font-bold"
                  >{group.title}</span
                >
                <div class="grid grid-cols-1 gap-2 m-2">
                  {#each group.params as param}
                    <div>
                      <Label for="first_name" class="mb-2">
                        {param.name}: {param.value}
                      </Label>
                    </div>
                  {/each}
                </div>
              </div>
              {#if index != groups.reduce((acc, g) => {
                  return acc + (g.advanced ? 1 : 0);
                }, 0) - 1}
                <Hr />
              {/if}
            {/each}
          </AccordionItem>
        </Accordion>
      </div>
      <div class="w-1/2 p-4">
        <Charts finetuneEntry={finetune_entry} {id} realTime={real_time} />
      </div>
    </div>
  </div>
{/if}
