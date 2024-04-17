<script lang="ts">
    import { Button } from "flowbite-svelte";
    export let link: string;
    export let avaliable: boolean;

    let iframe: HTMLIFrameElement;
</script>

{#if avaliable}
    <iframe bind:this={iframe} title={link} src={link} class="w-full h-[75vh]"></iframe>
{:else}
    <div class="text-center">
        <p>Deployment is not available</p>
    </div>
{/if}