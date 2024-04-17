<script lang="ts">
    import axios from "axios";
    import { onMount } from "svelte";
    import { getContext } from "svelte";
    import toFormatted from "../../utils/ConvertDatetimeString";
    import TaggedSearchbar from "./TaggedSearchbar.svelte";
    import { SearchOutline } from "flowbite-svelte-icons";
    import { Badge, Button } from "flowbite-svelte";
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

    let searchParams: SearchParams = {
        tags: [],
        start_time: "",
        end_time: "",
        limit: 99
    };

    const col_names = [t("fault.message"), t("fault.time"), t("fault.source"), t("fault.code"), t("fault.action")];

    onMount(async () => {
        const res = await axios.post("/api/fault", searchParams);
        faults = res.data;
    });

    let tags = [] as string[];

    async function handleSearch(event) {
        searchParams.tags = tags;
        console.log(searchParams)
        const res = await axios.post("/api/fault", searchParams);
        faults = res.data;
    }
</script>

<div class="overflow-x-auto">
    <div>
        <TaggedSearchbar bind:tags={tags}/>
    </div>
    <Button class="my-2" on:click={handleSearch}>
        <SearchOutline size="sm"/>
        {t("fault.search")}
    </Button>
    <table class="table-auto border-collapse w-full h-full">
        <thead>
            <tr class="rounded-lg text-sm font-medium text-gray-700 text-left" style="font-size: 0.9674rem">
                {#each col_names as name (name)}
                    <th class="px-4 py-2 bg-gray-200" style="background-color:#f8f8f8">{name}</th>
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
                        <a href={`/fault/log?id=${fault.id}`} class="text-blue-600 hover:underline">{t("fault.view_logs")}</a>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>