<script lang="ts">
  import axios from "axios";
  import { onMount } from "svelte";
  import { getContext } from "svelte";
  import toFormatted from "../../utils/ConvertDatetimeString";
  import TaggedSearchbar from "./TaggedSearchbar.svelte";
  import { SearchOutline } from "flowbite-svelte-icons";
  import { Badge, Button, Modal } from "flowbite-svelte";
  const t: any = getContext("t");

  interface SearchParams {
    tags: string[];
    start_time: string;
    end_time: string;
    limit: number;
  }

  interface Fault {
    id: number;
    time: string;
    source: string[];
    message: string;
    code: number;
  }

  let faults = [] as Fault[];
  let stop_modal = false;

  let searchParams: SearchParams = {
    tags: [],
    start_time: "",
    end_time: "",
    limit: 99,
  };

  const col_names = [
    t("fault.message"),
    t("fault.time"),
    t("fault.source"),
    t("fault.code"),
    t("fault.action"),
  ];

  onMount(async () => {
    const res = await axios.post("/api/fault", searchParams);
    faults = res.data;
  });

  let tags = [] as string[];

  async function handleSearch(event) {
    searchParams.tags = tags;
    console.log(searchParams);
    const res = await axios.post("/api/fault", searchParams);
    faults = res.data;
  }
</script>

<Modal title={t("fault.wordcloud")} bind:open={stop_modal} autoclose>
  <div class="">
    <img
      class="h-full w-full object-scale-down"
      src={`/api/fault/wordcloud`}
      alt=""
    />
  </div>

  <svelte:fragment slot="footer">
    <div class="w-full flex justify-end gap-2">

      <Button color="alternative">{t("fault.close")}</Button>
    </div>
  </svelte:fragment>
</Modal>

<div class="pt-2 w-full">
  <span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;{t("fault.title")}</span>
  <span class="text-1xl pt-2 text-black-400 text-center"
    >&nbsp;&nbsp;{t("fault.description")}</span
  >
</div>
<hr class="pt-1" />

<div class="overflow-x-auto">
  <div class="flex flex-row justify-between">
    <div class="flex w-full">    
      <div class="flex py-2 w-1/2 m-1">
        <TaggedSearchbar bind:tags />
      </div>
      <div class="flex m-1">
        <Button class="my-2" on:click={handleSearch}>
          <SearchOutline size="sm" />
          {t("fault.search")}
        </Button>
      </div>
    </div>
    <div class="flex m-1">
      <Button class="my-2" color="green" on:click={(_) => {
        stop_modal = true;
      }}>
        {t("fault.wordcloud")}
      </Button>
    </div>
  </div>
  <table class="table-auto border-collapse w-full h-full">
    <thead>
      <tr
        class="rounded-lg text-sm font-medium text-gray-700 text-left"
        style="font-size: 0.9674rem"
      >
        {#each col_names as name (name)}
          <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8"
            >{name}</th
          >
        {/each}
      </tr>
    </thead>
    <tbody class="text-sm font-normal text-gray-700">
      {#each faults as fault (fault.id)}
        <tr class="hover:bg-gray-100 rounded-lg">
          <td class="px-4 py-4 w-1/3">{fault.message}</td>
          <td class="px-4 py-4 w-[10%]">{toFormatted(fault.time)}</td>
          <td class="px-4 py-4 w-1/8">
            {#each fault.source as source (source)}
              <Badge rounded color="indigo" class="m-1">{source}</Badge>
            {/each}
          </td>
          <td class="px-4 py-4">{fault.code}</td>
          <td class="px-4 py-4">
            <a
              href={`/fault/log?id=${fault.id}`}
              class="text-blue-600 hover:underline">{t("fault.view_logs")}</a
            >
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
