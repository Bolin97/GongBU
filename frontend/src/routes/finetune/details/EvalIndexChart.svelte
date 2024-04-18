<script lang="ts">
  import axios from "axios";
  import { onDestroy, onMount } from "svelte";
  import { REALTIME_FINETUNE_DETAIL, UPDATE_VIEW_INTERVAL } from "../../store";
  import Chart from "../../components/Chart.svelte";

  export let name: string;
  export let displayName: string;
  export let title: string;
  export let id: string;
  export let state: number;

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

  let options = {
    ...line_options,
    series: [
      {
        name: displayName,
        data: [],
      },
    ],
    xaxis: {
      type: "numeric",
      label: "epoch",
    },
  };

  $: {
    options = {
      ...line_options,
      series: [
        {
          name: displayName,
          data: eval_raw.map((each) => {
            return {
              x: each.epoch,
              y: each.value,
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

  let eval_raw = [];
  let eval_update;
  onMount(async () => {
    eval_raw = (
      await axios.get(`/api/eval_index`, {
        params: {
          id: id,
          ind: name,
        },
      })
    ).data;
    eval_update = setInterval(async () => {
      if (!$REALTIME_FINETUNE_DETAIL) {
        return;
      }
      if (state == 0) {
        eval_raw = [
          ...eval_raw,
          ...(
            await axios.get(`/api/eval_index/after`, {
              params: {
                id: id,
                ind: name,
                after:
                  eval_raw.length == 0
                    ? -1
                    : eval_raw.at(eval_raw.length - 1).epoch,
              },
            })
          ).data,
        ];
      }
    }, UPDATE_VIEW_INTERVAL);
  });
  onDestroy(async () => {
    clearInterval(eval_update);
  });
  $: {
    options = {
      ...line_options,
      series: [
        {
          name: displayName,
          data: eval_raw.map((each) => {
            return { x: each.epoch, y: each.value };
          }),
        },
      ],
      xaxis: {
        type: "numeric",
        label: "epoch",
      },
    };
  }
</script>

<div class="m-1 p-2">
  <span class="text-1xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;{title}</span
  >
  <Chart {options} />
</div>
