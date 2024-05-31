<script lang="ts">
    import type DatasetEntry from "../../../class/DatasetEntry";
    import axios from "axios";
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import { getContext } from "svelte";
    const t: any = getContext("t");

    import DatasetTable from "../DatasetTable.svelte";
    import { Button, Range } from "flowbite-svelte";
    import ActionPageTitle from "../../components/ActionPageTitle.svelte";
    import { goto } from "$app/navigation";
    const poolId = $page.url.searchParams.get("pool_id");

    let entries: Array<DatasetEntry> = [];
    async function fetch_dataset_entries() {
        entries = (await axios.get(`/api/dataset_entry/by_pool/${poolId}`)).data;
    }
    onMount(async () => {
        await fetch_dataset_entries();
    })

    let selectedDatasetId: number | null = null;
    let reduce_to_percentage = 0.5;
    let name = `Sifted-${Date.now().toString().substring(5, 10)}`;
    let description = `Sifted-${Date.now().toString().substring(5, 10)}`;

    $: validForSumbit = name.length > 0 && selectedDatasetId !== null && reduce_to_percentage > 0 && reduce_to_percentage < 1;

    async function submit() {
        await axios.post(`/api/filter/kmeans`, {}, {
            params: {
                pool_id: poolId,
                name: name,
                description: description,
                source_entry_id: selectedDatasetId,
                reduce_to_percentage: reduce_to_percentage
            }
        })
        goto("/data");
    }
</script>

<ActionPageTitle returnTo={"/data"} title={t("data.filter.title")}/>

<div class="m-2 p-2">
    <span>{t("data.filter.p1")}</span>
    <DatasetTable datasetEntries={entries} noOperation={true} on:modified={async (_) => {
        await fetch_dataset_entries();
    }} selectable={true} bind:selectedDatasetId={selectedDatasetId}/>
</div>
<div class="m-2 p-2">
<span>{t("data.filter.p2")}</span>
<div class="w-full flex flex-row">
    <div class="w-7/12 flex-row">
        <div class="relative w-full mx-2">
            <input
                type="range"
                bind:value={reduce_to_percentage}
                min={0}
                max={1}
                step={0.0001}
                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <span
                class="text-sm text-gray-500 dark:text-gray-400 absolute start-0 -bottom-6"
                >0</span
            >
            <span
                class="text-sm text-gray-500 dark:text-gray-400 absolute end-0 -bottom-6"
                >1</span
            >
        </div>
    </div>
    <div class="mx-8">
        <input
          type="number"
          aria-describedby="helper-text-explanation"
          class={`bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
          bind:value={reduce_to_percentage}
          min={0}
          max={1}
          step={0.0001}
        />
    </div>
</div>
</div>

<div class="m-2 p-2">
<span>{t("data.filter.name")}</span>
<input
    type="text"
    aria-describedby="helper-text-explanation"
    class={`bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
    bind:value={name}
/>
</div>

<div class="m-2 p-2">
<span>{t("data.filter.des")}</span>
<input
    type="text"
    aria-describedby="helper-text-explanation"
    class={`bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500`}
    bind:value={description}
/>
</div>

<div class="flex flex-row justify-end gap-2 mt-4">
    <Button
        on:click={submit}
        disabled={!validForSumbit}
    >
        {t("data.filter.begin")}
    </Button>
</div>