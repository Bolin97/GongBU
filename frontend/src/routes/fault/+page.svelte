<script lang="ts">
    import axios from "axios";
    import { onMount } from "svelte";

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

    onMount(async () => {
        const res = await axios.post("/api/fault", searchParams);
        faults = res.data;
    });
</script>

<div class="overflow-x-auto">
    <table class="min-w-full leading-normal">
        <thead>
            <tr>
                <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Message
                </th>
                <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Time
                </th>
                <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Source
                </th>
                <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Code
                </th>
                <th class="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Action
                </th>
            </tr>
        </thead>
        <tbody>
            {#each faults as fault (fault.id)}
                <tr>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        {fault.message}
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        {fault.time}
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        {fault.source.join(', ')}
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        {fault.code}
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        <a href={`/fault/log?id=${fault.id}`}>Check the log</a>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>