<script lang="ts">
    import { Hr } from "flowbite-svelte";


    import GoBack from "./GoBack.svelte";

    export let returnTo: string | null =  null;
    export let title: string;
    export let subtitle: string | "" = "";
</script>
<div class="flex flex-row justify-between">
    <div class="flex">
        {#if returnTo != "" && returnTo != null && returnTo != undefined && returnTo.length > 0}
            <GoBack returnTo={returnTo}/>
        {/if}
        <span class="text-2xl pt-1 text-black-400 font-bold">&nbsp;&nbsp;{title}</span>
        <span class="text-1xl pt-2 text-black-400 text-center" >&nbsp;&nbsp;{subtitle}</span>
        <slot name="left"/>
    </div>
    <div class="flex">
        <slot name="right"/>
    </div>
</div>
<hr class="mt-2 mb-4"/>