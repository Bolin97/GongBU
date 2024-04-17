<script lang="ts">
    import type FinetuneEntry from "../../class/FinetuneEntry";
    import type FinetuneEntryReduced from "../../class/FinetuneEntryReduced";
    import toFormatted from "../../utils/ConvertDatetimeString";
    import FinetuneProgess from "./FinetuneProgess.svelte";

    export let entry: FinetuneEntryReduced;
</script>

<div class="p-2 bg-white rounded-md overflow-hidden border shadow-sm shadow-gray-300 border-grey-300">
    <div class="p-2">
        <div class="tracking-wide text-sm text-blue-600 font-semibold">{entry.id} - {entry.name}</div>
        <p class="mt-2 text-gray-500">{toFormatted(entry.start_time)}</p>
        <div class="mt-2">
            {#if entry.state == -1}
                <div class="text-2xl font-bold">-</div>
            {:else}
                <FinetuneProgess id={entry.id.toString()} noUpdate={entry.state == 1}/>
            {/if}
        </div>
        <div class="mt-2">
            {#if entry.state == 0}
                训练中
            {:else if entry.state == 1}
                训练完成
            {:else if entry.state == -1}
                出错
            {:else}
                无效状态码
            {/if}
        </div>
        <p class="mt-2 text-gray-500">
            {entry.description}
            {#if entry.description == ""}
            &nbsp;
            {/if}
        </p>
        <div class="mt-2">
            <a href={`/finetune/details?finetune_id=${entry.id}`} class="text-blue-600 hover:underline">详细信息</a>
        </div>
    </div>
</div>