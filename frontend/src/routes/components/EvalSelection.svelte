<script lang="ts">
  export let indexes: Array<string>;
  import { getContext } from "svelte";
  const t: any = getContext("t");
  const presets = [
    {
      name: "Accuracy",
      value: "A",
      description: t("components.eval_metrics_description.acc_des"),
    },
    {
      name: "Recall",
      value: "R",
      description: t("components.eval_metrics_description.recall_des"),
    },
    {
      name: "F1-Score",
      value: "F",
      description: t("components.eval_metrics_description.f1score_des"),
    },
    {
      name: "Precision",
      value: "P",
      description: t("components.eval_metrics_description.pre_des"),
    },
    {
      name: "BLEU",
      value: "B",
      description: t("components.eval_metrics_description.bleu_des"),
    },
    {
      name: "Distinct-2",
      value: "D",
      description: t("components.eval_metrics_description.distinct_des"),
    },
  ];
</script>

<div class="flex flex-col bg-white p-6">
  {#each presets as index (index.value)}
    <label class="inline-flex items-center mt-3 border-b border-gray-200 pb-3">
      <input
        type="checkbox"
        class="form-checkbox h-5 w-5 text-gray-600 rounded checked:bg-blue-600 checked:border-blue-600"
        bind:group={indexes}
        value={index.value}
      />
      <span class="ml-4 text-lg font-semibold text-gray-700">{index.name}</span>
      <span class="ml-2 text-gray-500 text-sm font-medium"
        >{index.description}</span
      >
    </label>
  {/each}
</div>
