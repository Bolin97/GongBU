<script lang="ts">
  import axios from "axios";
  import type FinetuneEntry from "../../../class/FinetuneEntry";
  import { UPDATE_VIEW_INTERVAL } from "../../store";
  import { onDestroy, onMount } from "svelte";
  import type LoggingRecord from "../../../class/LoggingRecord";
  import type EvalRecord from "../../../class/EvalRecord";
  import Chart from "../../components/Chart.svelte";
  import type EvalIndex from "../../../class/EvalIndex";
  import { each } from "svelte/internal";
  import EvalIndexChart from "./EvalIndexChart.svelte";
  const tk_amount = 6;
  export let realTime: boolean = true;
  export let finetuneEntry: FinetuneEntry;
  export let id: string;

  const line_options = {
    chart: {
      type: "line",
    },
    xaxis: {
      type: "numeric",
      tickAmount: 5,
    },
    stroke: {
      curve: "straight",
      width: [2, 2, 2],
    },
  };

  let logging_records_updater: any;
  let logging_records = [] as Array<LoggingRecord>;
  onMount(async () => {
    async function update() {
      if (realTime) {
        if (finetuneEntry.state == 0) {
          logging_records = [
            ...logging_records,
            ...(
              await axios.get(`/api/logging/after/${id}`, {
                params: {
                  after:
                    logging_records.length == 0
                      ? -1
                      : logging_records.at(logging_records.length - 1).step,
                },
              })
            ).data,
          ];
        }
      }
    }
    logging_records = (await axios.get(`/api/logging/${id}`)).data;
    logging_records_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(logging_records_updater);
  });

  let eval_records_updater: any;
  let eval_records = [] as Array<EvalRecord>;
  onMount(async () => {
    async function update() {
      if (realTime) {
        if (finetuneEntry.state == 0) {
          eval_records = [
            ...eval_records,
            ...(
              await axios.get(`/api/logging/eval/after/${id}`, {
                params: {
                  after:
                    eval_records.length == 0
                      ? -1
                      : eval_records.at(eval_records.length - 1).epoch,
                },
              })
            ).data,
          ];
        }
      }
    }
    eval_records = (await axios.get(`/api/logging/eval/${id}`)).data;
    eval_records_updater = setInterval(update, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(() => {
    clearInterval(eval_records_updater);
  });

  $: {
    async function update() {
      options_loss = {
        ...line_options,
        series: [
          {
            name: "loss",
            data: logging_records.map((record) => {
              return {
                x: record.step,
                y: record.loss,
              };
            }),
          },
        ],
        xaxis: {
          type: "numeric",
          label: "step",
        },
      };
    }
    update();
  }

  $: {
    async function update() {
      options_eval_loss = {
        ...line_options,
        series: [
          {
            name: "loss",
            data: eval_records.map((record) => {
              return {
                x: record.epoch,
                y: record.loss,
              };
            }),
          },
        ],
        xaxis: {
          type: "numeric",
          label: "epoch",
        },
      };
    }
    update();
  }

  let options_loss = {
    ...line_options,
    series: [
      {
        name: "训练loss",
        data: [],
      },
    ],
    xaxis: {
      type: "numeric",
      label: "step",
    },
  };
  let options_eval_loss = {
    ...line_options,
    series: [
      {
        name: "loss",
        data: [],
      },
    ],
    xaxis: {
      type: "numeric",
      label: "epoch",
    },
  };

  let graphs = [];

  $: {
    async function update() {
      if (finetuneEntry.eval_step > 0 && finetuneEntry.val_set_size > 0) {
        graphs = [
          {
            title: "训练loss曲线",
            options: options_loss,
          },
          {
            title: "评估loss曲线",
            options: options_eval_loss,
          },
        ];
      } else {
        graphs = [
          {
            title: "训练loss曲线",
            options: options_loss,
          },
        ];
      }
    }
    update();
  }

  const eval_indexes = finetuneEntry.eval_indexes;

  import { eval_index_full_name } from "../../shared";
</script>

{#each graphs as graph}
  <div class="m-1 p-2">
    <span class="text-1xl pt-1 text-black-400 font-bold"
      >&nbsp;&nbsp;{graph.title}：</span
    >
    <Chart options={graph.options} />
  </div>
{/each}
{#each eval_indexes as eval_index}
  {#if eval_index.length != 0}
    <EvalIndexChart
      name={eval_index}
      displayName={eval_index_full_name[eval_index]}
      title={`${eval_index_full_name[eval_index]}曲线：`}
      {id}
      state={finetuneEntry.state}
    />
  {/if}
{/each}
