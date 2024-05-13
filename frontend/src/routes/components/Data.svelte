<script lang="ts">
  import axios from "axios";
  import { Select, Label } from "flowbite-svelte";
  import { getContext, onMount } from "svelte";
  import type PoolEntry from "../../class/PoolEntry";
  import type DatasetEntry from "../../class/DatasetEntry";
  interface ValueNamePair {
    value: string;
    name: string;
  }

  let selectedPool: string;
  export let selectedSet: string;
  const t: any = getContext("t");

  let pool_options = [] as Array<ValueNamePair>;
  onMount(async () => {
    const pools = (await axios.get(`/api/pool/`)).data as Array<PoolEntry>;
    pool_options = pools.map((entry) => {
      return {
        value: entry.id.toString(),
        name: entry.name,
      };
    });
  });
  let sets = [] as Array<ValueNamePair>;
  let loading = false;
  $: {
    if (selectedPool) {
      loading = true;
      axios.get(`/api/dataset_entry/by_pool/${selectedPool}`).then((res) => {
        sets = (res.data as Array<DatasetEntry>).map((entry) => {
          return {
            value: entry.id.toString(),
            name: entry.name,
          };
        });
        loading = false;
      });
    }
  }
</script>

<div class="m-4">
  <div class="m-4 my-8">
    <Label>
      {t("components.data.data_pool_selector")}
      <Select
        class="mt-2"
        items={pool_options}
        bind:value={selectedPool}
        placeholder={t("components.data.data_pool_des")}
      />
    </Label>
  </div>
  <div class={`m-4 my-8 ${loading ? "hidden" : ""}`}>
    <Label>
      {t("components.data.data_set_selector")}
      <Select
        class="mt-2"
        items={sets}
        bind:value={selectedSet}
        placeholder={t("components.data.data_set_des")}
      />
    </Label>
  </div>
</div>
